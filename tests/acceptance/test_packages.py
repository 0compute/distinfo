from __future__ import annotations

import dataclasses
import os
import pathlib
from typing import TYPE_CHECKING, ClassVar

import anyio
import atools
import httpx
import pytest
from box import Box

from distinfo import (
    DistCollector,
    Distribution as BaseDistribution,
    Requirement,
    Requires as BaseRequires,
    command,
    const,
    util,
)
from distinfo.base import DATACLASS_DEFAULTS

from ..cases import Case

if TYPE_CHECKING:
    from typing import Any

TEST_PACKAGES_DIR = f"/var/tmp/{const.NAME}-test-packages"  # noqa: S108

PYPI = "https://pypi.io/packages"

DEFAULT_BUILD_SYSTEM_REQUIRES = {
    Requirement.factory(reqstr) for reqstr in const.DEFAULT_BUILD_SYSTEM_REQUIRES
}

HERE = pathlib.Path(__file__).parent
PACKAGES = Box(util.loads((HERE / "test_packages.yaml").read_text()))
FIXTURES = []
for name, versions in PACKAGES.items():
    for version in list(versions):
        # version may be parsed as a float by the yaml loader
        str_version = str(version)
        # or Box() for empty package - used when adding tests
        versions[str_version] = versions.pop(version) or Box()
        versions[str_version].version = str_version
        # including version so it is included in the test name
        FIXTURES.append((name, str_version))


class TestPackages(Case):
    @pytest.mark.parametrize(("name", "version"), FIXTURES)
    async def test_collect(
        self,
        name: str,
        version: str,
        caplog: pytest.CaptureFixture,
        tmp_path: pytest.TempPathFactory,
    ) -> None:
        package = PACKAGES[name][version]
        if not package:  # pragma: no cover
            # marking todo
            pytest.skip()

        # set ext defaults to catch empty
        package.setdefault("ext", Box())
        for key in ("modules", "packages", "tests"):
            package.ext.setdefault(key, None)

        packages_dir = anyio.Path(TEST_PACKAGES_DIR)
        await packages_dir.mkdir(exist_ok=True)

        dir_name = f"{name}-{package.version}"
        archive = package.pop("archive", "tar.gz")
        if isinstance(archive, Box):
            # wheel dist
            archive_name = (
                f"{dir_name}-{archive.python}-{archive.abi}-{archive.platform}.whl"
            )
            url = f"{PYPI}/{archive.python}/{name[0]}/{name}/{archive_name}"
            package.ext.setdefault("format", "wheel")
        else:
            # source dist
            archive_name = f"{dir_name}.{archive}"
            url = f"{PYPI}/source/{name[0]}/{name}/{archive_name}"
            package.ext.setdefault("format", "pyproject")

        # get release archive
        archive_path = packages_dir / archive_name
        if not await archive_path.exists():  # pragma: no cover
            async with httpx.AsyncClient(follow_redirects=True) as client:
                response = await client.get(url)
            response.raise_for_status()
            await archive_path.write_bytes(response.content)

        # choose between using archive or extracted archive based on name first letter
        # oddness
        if archive_name.endswith(".whl") or ord(name[0]) % 2:
            path = archive_path
        else:
            # extract archive, not using builtin mods tarfile and zipfile as they are
            # not thread safe
            if archive_name.endswith(DistCollector.TAR_ARCHIVES):
                await command.run(
                    "tar",
                    f"--directory={tmp_path}",
                    "--extract",
                    "--file",
                    archive_path,
                )
            elif archive_name.endswith(DistCollector.ZIP_ARCHIVES):
                await command.run("unzip", "-d", tmp_path, archive_path)
            else:  # pragma: no cover
                pytest.fail(f"unsupported archive {archive}")
            path = anyio.Path(tmp_path) / dir_name

        options = dict(
            verbose=int(os.environ.get(util.envvar("verbose"), 0)), evaluate=True
        )
        options.update(package.pop("options", {}))

        # run it
        dist = await DistCollector.from_path(
            path,
            dist_cls=Distribution,
            options=options,
        )

        # remove default build system requires
        if "build_system_requires" in dist.requires:
            # FIXME: set(list(... why necessary?
            dist.requires.build_system_requires -= set(  # noqa: C414
                list(DEFAULT_BUILD_SYSTEM_REQUIRES)
            )

        self.log.debug(
            f"\n** test:\n{util.dumps(package)}\n"
            f"\n** dist:\n{util.dumps(dict(ext=dist.ext, requires=dist.requires))}"
        )

        logged = package.pop("logged", None)
        if logged is not None:
            assert logged in caplog.text

        # check requires
        package_requires = package.pop("requires", None)
        if package_requires is not None:
            for extra, reqs in package_requires.items():
                reqs = set(map(Requirement.factory, reqs))
                dist_reqs = dist.requires.pop(extra, set())
                assert reqs == dist_reqs, f"reqs diff for {extra!r}"
        assert (
            not dist.requires
        ), f"dist requires not empty:\n{util.dumps(dist.requires)}"

        # check everything else
        for key, value in package.items():
            self._assert_contains(key, value, getattr(dist, key))

    async def test_collect_self(self) -> None:
        # collect self to exercise git find files
        dist = await DistCollector.from_path(anyio.Path(HERE.parent.parent))
        assert dist.name == const.NAME
        assert dist.requires

    def _assert_contains(self, key: str, test: Any, dist: Any) -> None:
        if isinstance(test, dict):
            assert isinstance(dist, dict), f"key: {key}"
            for key, value in test.items():
                self._assert_contains(key, value, dist.get(key))
        else:
            if isinstance(test, list):
                test = set(test)
            assert test == dist, f"key: {key}"


class Requires(BaseRequires):
    # use a static environment for marker evaluation so these tests are deterministic
    @staticmethod
    @atools.memoize
    def _env() -> dict[str, str]:
        return {
            "implementation_name": "cpython",
            "implementation_version": "3.11.0",
            "os_name": "posix",
            "platform_machine": "x86_64",
            "platform_release": "6.2.1",
            "platform_system": "Linux",
            "platform_version": "#1-NixOS SMP PREEMPT_DYNAMIC",
            "python_full_version": "3.11.0",
            "platform_python_implementation": "CPython",
            "python_version": "3.11",
            "sys_platform": "linux",
        }


@dataclasses.dataclass(**DATACLASS_DEFAULTS)
class Distribution(BaseDistribution):
    REQUIRES_CLS: ClassVar[type] = Requires
