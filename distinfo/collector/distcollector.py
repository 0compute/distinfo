from __future__ import annotations

import contextlib
import dataclasses
import os
import subprocess
from typing import TYPE_CHECKING, ClassVar, overload

import anyio
import deepmerge
from box import Box

from .. import command, const, util
from ..base import DATACLASS_DEFAULTS, Base
from ..distribution import Distribution
from .cargo import Cargo
from .collector import Collector, CollectorMixin
from .findpackages import FindPackages
from .findtests import FindTests
from .metadata import (
    PathMetadata,
    PyProjectDynamicMetadata,
    PyProjectMetadata,
    SetuptoolsMetadata,
    dirty,
)

if TYPE_CHECKING:
    from typing import Literal

    from ..distribution import BaseDistribution, DistributionKeyType

    DistCollectorOptionsType = dict[str, int | tuple[str, ...]] | None


@dataclasses.dataclass(**DATACLASS_DEFAULTS)
class DistCollector(CollectorMixin, Base):
    DEFAULT_OPTIONS: ClassVar[Box] = Box(
        include=(),
        exclude=(),
        modify_globals=False,
        evaluate=False,
        verbose=0,
    )

    TAR_ARCHIVES: ClassVar[tuple[str, ...]] = (".tar.bz2", ".tar.gz", ".tar.xz")

    ZIP_ARCHIVES: ClassVar[tuple[str, ...]] = (".whl", ".zip")

    ARCHIVES: ClassVar[tuple[str, ...]] = (*TAR_ARCHIVES, *ZIP_ARCHIVES)

    dist: BaseDistribution

    path: anyio.Path

    files: list[str]

    options: Box

    @classmethod
    async def from_path(
        cls,
        path: anyio.Path | str,
        options: DistCollectorOptionsType = None,
        **kwargs: DistributionKeyType,
    ) -> BaseDistribution:
        if isinstance(path, str):
            path = anyio.Path(path)
        path = await path.resolve()

        ext = Box(path=str(path))

        with util.log_duration(f"from path: {path}", level="verbose"):
            async with util.tmpdir() if path.name.endswith(
                cls.ARCHIVES
            ) else contextlib.nullcontext() as tmpdir:
                if path.suffix == ".whl":
                    ext.format = "wheel"

                # extract archive
                if isinstance(tmpdir, str):
                    # path is an archive
                    if path.name.endswith(cls.TAR_ARCHIVES):
                        try:
                            files = await command.run(
                                "tar",
                                f"--directory={tmpdir}",
                                "--extract",
                                "--verbose",
                                "--file",
                                path,
                                lines=True,
                            )
                        except (
                            command.CalledProcessError
                        ) as exc:  # pragma: no ptest cover
                            if exc.returncode == 2:
                                raise FileNotFoundError(path) from None
                            raise
                        # "--verbose" flag lists directories as well as files - we don't
                        # want directories
                        files = [path for path in files if not path.endswith(os.sep)]
                    else:
                        try:
                            files = await command.run(
                                "unzip", "-d", tmpdir, path, lines=True
                            )
                        except (
                            command.CalledProcessError
                        ) as exc:  # pragma: no ptest cover
                            if exc.returncode == 9:
                                raise FileNotFoundError(path) from None
                            raise
                        prefix_length = len(tmpdir) + 1
                        files = [
                            # unzip prints "inflating: path" or "creating: dir/"
                            path.split()[1][prefix_length:]
                            # first file is archive name
                            for path in files[1:]
                            if not path.endswith(os.sep)
                        ]
                    path = anyio.Path(tmpdir)
                    # if the archive extracted to a common prefix then use it as source
                    # root
                    prefix = os.path.commonpath(files)
                    if prefix:
                        path /= prefix
                        prefix_length = len(prefix) + 1
                        files = [path[prefix_length:] for path in files]
                    files = await cls._filter_files(files)
                # path is a directory
                else:
                    files = await cls._find_files(path)

                if not files:  # pragma: no cover - error path
                    raise FileNotFoundError(f"{path} is empty")
                cls.clog.spam(f"files: {util.irepr(sorted(files), repr=str)}")

                if "ext" in kwargs:  # pragma: no ptest cover
                    deepmerge.always_merger.merge(kwargs["ext"], ext)
                else:
                    kwargs["ext"] = ext

                return await cls.from_dir(path, files, options=options, **kwargs)  # type: ignore[arg-type]

    @classmethod
    async def from_dir(
        cls,
        path: anyio.Path,
        files: list[str],
        *,
        collector: str | None = None,
        dist_cls: type[Distribution] = Distribution,
        options: DistCollectorOptionsType = None,
        **kwargs: DistributionKeyType,
    ) -> BaseDistribution:  # pragma: no utest ftest cover
        self = await cls.factory(
            path, files, dist_cls=dist_cls, options=options, **kwargs
        )

        if collector is not None:
            # run single dirty collector
            await self._collector(getattr(dirty, collector))
        else:
            # run all collectors
            async with anyio.create_task_group() as tg:
                tg.start_soon(self._collect_metadata)
                tg.start_soon(self._collector, FindTests)
                if self.dist.ext.get("format") != "wheel":
                    tg.start_soon(self._collector, Cargo)

        if self.options.evaluate:
            await self.dist.requires.evaluate()

        return self.dist

    @classmethod
    async def factory(
        cls,
        path: anyio.Path,
        files: list[str],
        *,
        dist_cls: type[Distribution] = Distribution,
        options: DistCollectorOptionsType = None,
        **kwargs: DistributionKeyType,
    ) -> DistCollector:  # pragma: no utest ftest cover
        _options = cls.DEFAULT_OPTIONS.copy()
        if options is not None:  # pragma: no ptest cover
            deepmerge.always_merger.merge(_options, Box(options))
        dist = await dist_cls.factory(
            _include=_options.include, _exclude=_options.exclude, **kwargs
        )
        return cls(options=_options, dist=dist, path=path, files=files)

    async def _collect_metadata(self) -> None:
        pyproject = await self._collector(PyProjectMetadata, call=False)
        setuptools = await self._collector(SetuptoolsMetadata, call=False)
        # run pyproject collector(s) if pyproject.toml exists
        if pyproject.exists:
            pyproject_result = await pyproject()
            # run dynamic collector if required, setuptools.build_meta is redundant
            # since we use the setuptools collector
            if not setuptools.exists and (
                (not pyproject_result and "build_backend" in self.dist.ext)
                or self.dist.dynamic
            ):
                await self._collector(PyProjectDynamicMetadata)
        # run setuptools collector if setup.py and/or setup.cfg exists
        if setuptools.exists:
            await setuptools()
            # format may be pyproject with setuptools.build_meta backend so don't
            # overwrite
            self.dist.ext.setdefault("format", "setuptools")
        async with anyio.create_task_group() as tg:
            tg.start_soon(self._collector, PathMetadata)
            # run path packages collector if modules and packages not set
            if not ("modules" in self.dist.ext or "packages" in self.dist.ext):
                tg.start_soon(self._collector, FindPackages)

    @overload
    async def _collector(self, cls: type[Collector]) -> bool:
        ...

    @overload
    async def _collector(self, cls: type[Collector], call: Literal[True]) -> bool:
        ...

    @overload
    async def _collector(self, cls: type[Collector], call: Literal[False]) -> Collector:
        ...

    async def _collector(
        self,
        cls: type[Collector],
        *,
        call: bool = True,
    ) -> Collector | bool:
        collector = cls(collector=self)
        if call:
            return await collector()
        return collector

    @classmethod
    async def _find_files(cls, path: anyio.Path) -> list:
        files = None
        if not util.is_tmpdir(path) and await (path / ".git").exists():
            try:
                files = await command.run(
                    "git",
                    "-C",
                    path,
                    "ls-files",
                    "--cached",
                    "--exclude-standard",
                    "--others",
                    "--directory",
                    lines=True,
                )
            except (
                subprocess.CalledProcessError
            ) as exc:  # pragma: no cover - error path
                if exc.returncode == 128:
                    raise FileNotFoundError(path) from None
                cls.clog.debug(f"git files fail: {exc}")
        if files is None:
            try:
                files = await command.run("find", "-type", "f", lines=True, cwd=path)
            except command.CalledProcessError as exc:  # pragma: no cover - error path
                if exc.returncode == 1:
                    raise FileNotFoundError(path) from None
                raise
            # files are prefixed "./"
            files = [path[2:] for path in files]
        return await cls._filter_files(files)

    @staticmethod
    async def _filter_files(
        files: list[str],
    ) -> list[str]:
        for directory in const.IGNORE_DIR_NAMES:
            files = [
                path
                for path in files
                if directory != path and f"{directory}/" not in path
            ]
        return files

    CONFTEST: ClassVar[str] = "conftest.py"

    PY_INIT: ClassVar[tuple[str, ...]] = (
        *(f"__init__{suffix}" for suffix in Collector.PY_SUFFIXES),
        *(f"__main__{suffix}" for suffix in Collector.PY_SUFFIXES),
        CONFTEST,
    )

    @util.cached_property
    def packages(self) -> list[str]:
        packages = []
        for path in self.sorted_files:
            if os.sep in path and path.endswith(self.PY_INIT):
                parts = path.split(os.sep)
                name = parts[-2]
                if name.startswith("_") or name in const.IGNORE_DIR_NAMES:
                    continue
                package = os.sep.join(parts[:-1])
                if name not in const.TEST_DIR_NAMES and len(parts) > 2:
                    # we only want root packages
                    parents = parts[:-2]
                    skip = False
                    while parents:
                        if os.sep.join(parents) in packages:
                            skip = True
                            break
                        parents.pop()
                    if skip:
                        continue
                packages.append(package)
        return packages

    @util.cached_property
    def non_test_packages(self) -> list[str]:
        return [
            path
            for path in self.packages
            if path.split(os.sep)[-1]
            not in (*const.TEST_DIR_NAMES, *self.dist.ext.get("tests", []))
        ]

    @util.cached_property
    def sorted_files(self) -> list[str]:
        return sorted(self.files, key=len)
