from __future__ import annotations

import dataclasses
import functools
import os
from fnmatch import fnmatch

import anyio

from .. import const, monkey, util
from ..base import DATACLASS_DEFAULTS
from .collector import Collector
from .findtests import FindTests


@dataclasses.dataclass(**DATACLASS_DEFAULTS)
class FindPackages(Collector):
    async def _collect(self) -> bool:
        from setuptools import Distribution as SetuptoolsDistribution
        from setuptools.discovery import ConfigDiscovery
        from setuptools.errors import PackageDiscoveryError

        monkey.patch_setuptools()
        dist = SetuptoolsDistribution(dict(src_root=self.path))
        discovery = ConfigDiscovery(dist)
        try:
            await anyio.to_thread.run_sync(functools.partial(discovery, name=False))
        except PackageDiscoveryError as exc:
            self.log.debug(f"config discovery fail: {exc}")
            return await self._collect_fallback()
        else:
            self.log.debug("setting packages from setuptools discovery")
            await self.packages_from_setuptools_dist(dist)
            return True

    async def _collect_fallback(self) -> bool:
        # modules/packages
        if self.non_test_packages:
            packages = {path.split(os.sep)[-1] for path in self.non_test_packages}
            self.log.debug(f"setting packages: {util.irepr(packages, repr=str)}")
            self.dist.ext.packages = packages
        else:  # pragma: no ptest cover
            util.raise_on_hit()
            modules = {
                anyio.Path(path).stem
                for path in self.files
                if os.sep not in path
                and path.endswith(self.PY_SUFFIXES)
                and path != const.SETUP_PY
                and not fnmatch(path.split(os.sep)[-1], FindTests.FILE_GLOB)
            }
            if modules:  # pragma: no branch
                self.log.debug(f"setting modules: {util.irepr(modules, repr=str)}")
                self.dist.ext.modules = modules
            else:
                return False
        return True
