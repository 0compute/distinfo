from __future__ import annotations

from typing import TYPE_CHECKING

import anyio

from distinfo import const, util
from distinfo.collector import DistCollector

from ..cases import Case as BaseCase

if TYPE_CHECKING:
    from typing import Any

    from collecions.abc import Callable
    from py.path import local

    from distinfo import Requires
    from distinfo.collector import Collector
    from distinfo.collector.distcollector import DistCollectorOptionsType
    from distinfo.distribution import DistributionKeyType

SETUP = """
from setuptools import setup
setup()
"""

PYPROJECT = """
[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"
[project]
name = "aproject"
version = "1"
dependencies = ["xxx"]
[project.optional-dependencies]
aaa = ["bbb"]
"""


class Case(BaseCase):
    collector: type[Collector]

    def _write_setup(self, tmpdir: local, setup: str = SETUP) -> local:
        tmpdir.join(const.SETUP_PY).write(setup)

    def _write_pyproject(self, tmpdir: local, pyproject: str = PYPROJECT) -> local:
        tmpdir.join(const.PYPROJECT_TOML).write(pyproject)

    def _write_module(
        self, tmpdir: local, name: str = "xxx", content: str = ""
    ) -> local:
        tmpdir.join(f"{name}.py").write(content)

    def _write_package(
        self,
        tmpdir: local,
        name: str = "xxx",
        *,
        mod_name: str = "__init__",
        content: str = "",
    ) -> local:
        package = tmpdir.join(name).mkdir()
        self._write_module(package, mod_name, content)
        return package

    async def _mk_collector(
        self,
        path: local,
        *,
        cls: type[Collector] | None = None,
        options: DistCollectorOptionsType = None,
        **kwargs: DistributionKeyType,
    ) -> Collector:
        if cls is None:
            cls = self.collector
        path = anyio.Path(path)
        files = await DistCollector._find_files(path)
        distcollector = await DistCollector.factory(
            path, files, options=options, **kwargs
        )
        return cls(collector=distcollector)

    async def _collect(
        self,
        path: local,
        collector: Collector | None = None,
        *,
        fail: bool = False,
        options: DistCollectorOptionsType = None,
        **kwargs: DistributionKeyType,
    ) -> tuple[Collector, Requires]:
        if collector is None:
            collector = await self._mk_collector(path, options=options, **kwargs)
        result = await collector()
        assert not result if fail else result
        util.clean_dict(collector.dist.ext, inplace=True)
        return collector, await collector.dist.requires.evaluate()

    @staticmethod
    def _raiser(cls: type[BaseException], arg: str = "fail") -> Callable:
        def raiser(*_args: Any, **_kwargs: Any) -> None:
            raise cls(arg)

        return raiser
