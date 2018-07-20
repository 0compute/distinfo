from __future__ import annotations

from typing import TYPE_CHECKING, cast

from distinfo.collector import PyProjectDynamicMetadata, PyProjectMetadata

from .cases import Case

if TYPE_CHECKING:
    from py.path import local

    from distinfo import Requires
    from distinfo.collector import Collector
    from distinfo.distribution import DistributionKeyType

PYPROJECT = """
[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"

[project]
name = "xxx"
version = "1"
dynamic = ["dependencies"]

[project.optional-dependencies]
dev = ["aaa"]
"""

PYPROJECT_FLIT = """
[build-system]
requires = ["flit-core", "zzz"]
build-backend = "flit_core.buildapi"

[tool.flit.metadata]
author = "a"
module = "aaa"
requires=["yyy"]

[tool.flit.metadata.requires-extra]
aaa = ["bbb"]
"""


class TestPyProjectDynamicMetadata(Case):
    collector = PyProjectDynamicMetadata

    async def _mk_collector(  # type: ignore[override]
        self,
        path: local,
        **kwargs: DistributionKeyType,
    ) -> PyProjectDynamicMetadata:
        pyprojectmetadata_collector = await super()._mk_collector(
            path, cls=PyProjectMetadata, **kwargs
        )
        await pyprojectmetadata_collector()
        collector = cast(
            PyProjectDynamicMetadata,
            await super()._mk_collector(path, **kwargs),
        )
        collector.dist = pyprojectmetadata_collector.dist
        return collector

    def _assert_basic(self, collector: Collector, requires: Requires) -> None:
        assert collector.dist.name == "xxx"
        assert "run" not in requires
        assert requires.dev == {"aaa"}

    async def test_collect(self, tmpdir: local) -> None:
        self._write_pyproject(tmpdir, PYPROJECT)
        self._write_package(tmpdir, "aaa")
        # basic
        collector, requires = await self._collect(tmpdir)
        self._assert_basic(collector, requires)
        # subprocess
        collector, requires = await self._collect(
            tmpdir, options=dict(modify_globals=False)
        )
        self._assert_basic(collector, requires)

    async def test_collect_flit(self, tmpdir: local) -> None:
        self._write_pyproject(tmpdir, PYPROJECT_FLIT)
        self._write_package(tmpdir, "aaa", content='"""x"""\n__version__="1"')
        collector, requires = await self._collect(tmpdir)
        assert collector.dist.name == "aaa"
        assert requires.run == {"yyy"}
        assert requires.aaa == {"bbb"}
