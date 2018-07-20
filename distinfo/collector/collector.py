from __future__ import annotations

import dataclasses
import logging
import os
from fnmatch import fnmatch
from typing import TYPE_CHECKING, ClassVar

from .. import const, util
from ..base import DATACLASS_DEFAULTS, Base

if TYPE_CHECKING:
    from typing import Any

    from setuptools.dist import Distribution as SetuptoolsDistribution

    from ..distribution import BaseDistribution
    from .distcollector import DistCollector

log = logging.getLogger(__name__)


class CollectorMixin:
    dist: BaseDistribution

    def __str__(self) -> str:  # pragma: no ptest cover
        return str(self.dist)


@dataclasses.dataclass(**DATACLASS_DEFAULTS)
class Collector(CollectorMixin, Base):
    collector: DistCollector

    result: bool | None = None

    @property
    def exists(self) -> bool:
        raise NotImplementedError

    def __getattr__(self, key: str) -> Any:
        return getattr(self.collector, key)

    async def __call__(self) -> bool:
        with self.log.duration(
            "collecting...",
            lambda: self.result and "success" or "failure",
            level="verbose",
        ):
            self.result = await self._collect()
            return self.result

    async def _collect(self) -> bool:
        raise NotImplementedError

    PY_SUFFIXES: ClassVar[tuple[str, ...]] = tuple(
        f".{suffix}" for suffix in ("py", "pyi", "pyx")
    )

    async def packages_from_setuptools_dist(self, dist: SetuptoolsDistribution) -> None:
        # modules
        if dist.py_modules:
            modules = set()
            for module in dist.py_modules:
                # ext modules come as tuples
                if isinstance(module, tuple):  # pragma: no ftest cover
                    module = module[0]
                # check it exists
                if self._package_filter(module) and [
                    path
                    for path in self.sorted_files
                    if fnmatch(path.split(os.sep)[-1], f"{module}.p*")
                ]:
                    modules.add(module)
            if modules:  # pragma: no branch
                self.log.debug(f"set modules: {util.irepr(modules, repr=str)}")
                self.dist.ext.setdefault("modules", set()).update(modules)
        # packages
        if dist.packages:
            await self.set_packages(set(dist.packages))

    async def set_packages(self, packages: set[str]) -> None:
        from setuptools.discovery import find_parent_package

        parent_pkg = find_parent_package(packages, {}, self.path)
        if parent_pkg is not None:
            packages = {parent_pkg}
        # make sure they are really packages
        for package in list(packages):
            if not self._package_filter(package):
                packages.remove(package)
            else:
                path = os.sep.join(package.split("."))
                for package_path in self.non_test_packages:
                    if package_path.endswith(path):
                        break
                else:
                    packages.remove(package)
        if packages:
            self.log.debug(f"set packages: {util.irepr(packages, repr=str)}")
            self.dist.ext.setdefault("packages", set()).update(packages)

    PACKAGE_IGNORE: ClassVar[tuple[str, ...]] = (
        "_",
        *const.IGNORE_DIR_NAMES,
        *const.TEST_DIR_NAMES,
    )

    def _package_filter(self, package: str) -> bool:
        if package.startswith("_"):
            return False
        return all(
            not part.startswith(self.PACKAGE_IGNORE) for part in package.split(".")
        )
