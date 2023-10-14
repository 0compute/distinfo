from __future__ import annotations

import contextlib
import ctypes
import dataclasses
import functools
import io
import itertools
import logging
import os
import sys
import warnings
from typing import TYPE_CHECKING, ClassVar

import anyio

from .... import command, const, monkey, util
from ....base import DATACLASS_DEFAULTS
from .dirtycollector import DirtyCollector

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Generator
    from typing import Any

    from setuptools._importlib import EntryPoints, SelectableGroups
    from setuptools.dist import Distribution as SetuptoolsDistribution

log = logging.getLogger(__name__)


@dataclasses.dataclass(**DATACLASS_DEFAULTS)
class SetuptoolsMetadata(DirtyCollector):
    # NOTE: this modifies global state by:
    #  - changing directory
    #  - patching distutils and setuptools
    #  - redirecting sys.stdout
    #  - setting warning filters

    EXTRA_MAP: ClassVar[dict[str, str]] = dict(
        install_requires=const.RUN_EXTRA,
        setup_requires=const.BUILD_SYSTEM_EXTRA,
        tests_require=const.TEST_EXTRA,
    )

    # sys.argv[1] for setup script, it can't be empty, this seems all-round safest
    SETUP_PY_ARG: ClassVar[str] = "sdist"

    @util.cached_property
    def setup_py_exists(self) -> bool:
        # files is None when run in subprocess - check has happened already
        return const.SETUP_PY in self.files

    @util.cached_property
    def exists(self) -> bool:
        return self.setup_py_exists or const.SETUP_CFG in self.files

    async def _collect_dirty(self) -> bool:
        monkey.patch_setuptools()

        import distutils.core

        import setuptools
        from setuptools import SetuptoolsDeprecationWarning, sandbox
        from setuptools.dist import Distribution as SetuptoolsDistribution

        async with self._working_copy():
            with (
                contextlib.chdir(self.path),
                sandbox.save_pkg_resources_state(),
                sandbox.save_argv(),
                sandbox.save_path(),
                self._save_modules(),
                self._patch(distutils.core, "setup", self.setup),
                self._patch(setuptools, "setup", self.setup),
                self._patch(
                    SetuptoolsDistribution,
                    "finalize_options",
                    functools.partialmethod(_finalize_options, log=self.log),
                ),
                self._redirect_stdout(),
            ):
                # filter warnings
                warnings.filterwarnings("ignore", category=DeprecationWarning)
                warnings.filterwarnings("ignore", category=UserWarning)
                warnings.filterwarnings(
                    "ignore", "Unknown distribution option", module="distutils.dist"
                )
                # is not derived from DeprecationWarning because ¯\_(ツ)_/¯
                warnings.filterwarnings("ignore", category=SetuptoolsDeprecationWarning)
                try:
                    from setuptools.config.pyprojecttoml import _BetaConfiguration
                except ImportError:  # pragma: no cover
                    ...
                else:
                    warnings.filterwarnings("ignore", category=_BetaConfiguration)

                # setup.py absolute path
                setup_py = self.path / const.SETUP_PY
                setup_py_str = str(setup_py)

                # write a bare setup.py if none exists - this happens with
                # setuptools.build_meta and setup.cfg
                if not self.setup_py_exists:
                    await setup_py.write_text("__import__('setuptools').setup()")
                    self.log.debug(f"wrote bare {const.SETUP_PY}")

                # run the script
                sys.argv[:] = [const.SETUP_PY, self.SETUP_PY_ARG]
                sys.path.insert(0, str(self.path))
                for where in self.dist.ext.get("where", ["."]):
                    sys.path.insert(0, str(self.path / where))
                    try:
                        sandbox._execfile(
                            setup_py_str,
                            dict(__file__=setup_py_str, __name__="__main__"),
                        )
                    except (Exception, SystemExit) as exc:
                        self._log_build_exc(exc)
                    else:
                        break
                else:
                    return False

        if self.stdist is None:  # pragma: no cover
            util.raise_on_hit()
            self.log.warning("setup not run")
            return False

        # license, may be empty string (dovado-0.4.0) or the builtin func
        # (maxcube-api-0.4.3)
        license: Any = self.stdist.metadata.license
        if license is not None and not isinstance(license, str):
            self.log.warning(f"Unsupported license type {type(license)!r}")
            license = None
        license_files = self.stdist.metadata.license_files
        # drop license_files as not required
        self.stdist.metadata.license_files = []
        # if no license pick the first license file, sorted to be deterministic
        if not license and license_files:
            await self._try_set_license(self.stdist.metadata, sorted(license_files)[0])
        # if license is a single line it may be a file reference
        elif license and "\n" not in license:
            await self._try_set_license(self.stdist.metadata, license)

        # metadata
        stream = io.StringIO()
        self.stdist.metadata.write_pkg_file(stream)
        await self.update_from_pkginfo(stream.getvalue())

        # packages/modules
        await self.packages_from_setuptools_dist(self.stdist)

        # requirements
        for attr, extra in self.EXTRA_MAP.items():
            await self._add_requirements(extra, getattr(self.stdist, attr, None) or [])
        extras: dict[str, set] = {}
        for extra, reqs in getattr(self.stdist, "extras_require", {}).items():
            # parse request condition from setuptools "extra:condition" syntax
            try:
                extra, condition = extra.split(":", 1)
            except ValueError:
                pass
            else:
                reqs = [f"{req}; {condition}" for req in reqs]
            extras.setdefault(extra or const.RUN_EXTRA, set()).update(reqs)
        for extra, reqs in sorted(extras.items(), key=lambda item: item[0]):
            await self._add_requirements(extra, reqs)

        # test config
        # XXX: wanted? useful?
        for key in ("loader", "runner", "suite"):
            value = getattr(self.stdist, f"test_{key}")
            if value is not None:
                self.log.debug(f"setuptools_test.{key} = {value!r}")
                self.dist.ext.setdefault("setuptools_test", {})[key] = value
                if key != "suite":  # pragma: no cover
                    util.raise_on_hit()

        # extended metadata
        if self.stdist.entry_points is not None:
            if isinstance(self.stdist.entry_points, dict):
                for key, value in self.stdist.entry_points.items():
                    if isinstance(value, str):  # pragma: no ftest cover
                        value = [value]
                    self.dist.ext.setdefault("entrypoints", {})[key] = dict(
                        [v.strip() for v in v.split("=")] for v in value
                    )
            else:
                self.log.warning(
                    f"entry_points not a dict: {self.stdist.entry_points!r}"
                )
        if self.stdist.scripts is not None:
            self.dist.ext["scripts"] = self.stdist.scripts

        return True

    def _subprocess_cmd_hook(self, cmd: list[str]) -> None:
        if "where" in self.dist.ext:
            cmd.extend(("--set", f"ext.where:@{','.join(self.dist.ext.where)}"))

    async def _add_requirements(
        self, extra: str, reqs: list[str] | set[str] | str
    ) -> None:
        # fix reqs specified as str
        if isinstance(reqs, str):
            reqs = [reqs]
        # fix reqs that contain a comment (comes from pbr reading requirements.txt)
        if reqs := [r for r in [r.split("#")[0].strip() for r in reqs] if r]:
            await super(SetuptoolsMetadata, self).add_requirements(extra, *reqs)

    @contextlib.asynccontextmanager
    async def _working_copy(self) -> AsyncGenerator[None, None]:
        # copy to a tmp dir unless self.path already is a tmp dir because we started
        # with an archive
        if util.is_tmpdir(self.path):
            yield  # pragma: no ftest cover
        else:
            async with util.tmpdir() as tmpdir:
                # keep reference to self.path for finally clause
                path = self.path
                await command.run("cp", "--archive", self.path, tmpdir)
                self.path = anyio.Path(tmpdir) / path.name
                await command.run("chmod", "--recursive", "u+w", self.path)
                try:
                    yield
                finally:
                    self.path = path

    @staticmethod
    @contextlib.contextmanager
    def _save_modules() -> Generator[None, None, None]:
        # modified from setuptools.sandbox to not mess with exceptions
        pre = sys.modules.copy()
        try:
            yield
        finally:
            sys.modules.update(pre)
            for module in list(sys.modules):
                if module not in pre:
                    del sys.modules[module]

    @contextlib.contextmanager
    def _patch(
        self, target: object, attr: str, patch: Any
    ) -> Generator[None, None, None]:
        orig = getattr(target, attr)
        setattr(target, attr, patch)
        try:
            yield
        finally:
            setattr(target, attr, orig)

    @contextlib.contextmanager
    def _redirect_stdout(self) -> Generator[None, None, None]:
        # really redirect stdout, based on
        # https://eli.thegreenplace.net/2015/redirecting-all-kinds-of-stdout-in-python/

        # pytest capture doesn't play nice with this so disable for ftest
        if os.environ.get("PYTEST_CURRENT_TEST", "").startswith("tests/functional"):
            with self._patch(sys, "stdout", sys.stderr):
                yield
                return

        original_stdout_fd = sys.stdout.fileno()

        def _redirect_stdout(to_fd: int) -> None:
            libc = ctypes.CDLL(None)
            c_stdout = ctypes.c_void_p.in_dll(libc, "stdout")
            libc.fflush(c_stdout)
            sys.stdout.close()
            os.dup2(to_fd, original_stdout_fd)

        saved_stdout_fd = os.dup(original_stdout_fd)
        try:
            _redirect_stdout(sys.stderr.fileno())
            sys.stdout = LogStream(os.fdopen(original_stdout_fd, "wb"))
            yield
            _redirect_stdout(saved_stdout_fd)
            sys.stdout = io.TextIOWrapper(os.fdopen(original_stdout_fd, "wb"))

        finally:
            os.close(saved_stdout_fd)

    def setup(self, **attrs: Any) -> SetuptoolsDistribution | None:
        from distutils.errors import DistutilsOptionError

        from setuptools.dist import Distribution as SetuptoolsDistribution

        # a cut-down version of distutils.core.setup that uses no globals and
        # always returns a Distribution
        #
        # - not using distutils.core.run_setup cos it swallows SystemExit which
        #   we want to know about
        # - not using setuptools.sandbox.run_setup cos it does it in a directory sandbox
        #   that we don't need and causes problems by patching tempfile
        attrs["script_name"] = const.SETUP_PY
        attrs["script_args"] = [self.SETUP_PY_ARG]
        try:
            self.stdist = SetuptoolsDistribution(attrs)
            self.stdist.parse_config_files()
        except (
            ValueError,
            DistutilsOptionError,
        ) as exc:  # pragma: no cover
            util.raise_on_hit()
            self._log_build_exc(exc)
        return self.stdist


# modified from SetuptoolsDistribution.finalize_options to catch DistutilsSetupError
def _finalize_options(self: SetuptoolsDistribution, log: logging.Logger) -> None:
    from distutils.errors import DistutilsSetupError

    from setuptools._importlib import metadata

    group = "setuptools.finalize_distribution_options"

    def by_order(hook: EntryPoints | SelectableGroups) -> int:
        return getattr(hook, "order", 0)

    defined = metadata.entry_points(group=group)
    filtered = itertools.filterfalse(self._removed, defined)
    loaded = map(lambda e: e.load(), filtered)  # noqa: C417 - sic. original
    for ep in sorted(loaded, key=by_order):
        try:
            ep(self)
        except DistutilsSetupError as exc:
            log.warning(f"setup error: {exc}")


class LogStream(io.TextIOWrapper):
    def write(self, text: str) -> int:
        lines = text.splitlines()
        for line in lines:
            line = line.rstrip()
            if line:
                log.warning(line)
        return len(lines)
