from __future__ import annotations

from typing import TYPE_CHECKING

from distinfo.collector import FindPkgs

from .cases import Case

if TYPE_CHECKING:
    from py.path import local


class TestFindPkgs(Case):
    collector = FindPkgs

    async def test_collect_empty(self, tmpdir: local) -> None:
        collector, _requires = await self._collect(tmpdir)
        for key in ("modules", "packages"):
            assert key not in collector.dist.ext

    async def test_collect_pkgs(self, tmpdir: local) -> None:
        aaa = self._write_package(tmpdir, "aaa")
        self._write_package(aaa, "bbb")
        self._write_package(tmpdir, "ccc")
        self._write_package(tmpdir, "example")
        collector, _requires = await self._collect(tmpdir)
        assert collector.dist.ext.packages == {"aaa", "ccc"}
        self._write_package(tmpdir, "ddd")
        collector, _requires = await self._collect(tmpdir)
        assert collector.dist.ext.packages == {"aaa", "ccc", "ddd"}

    async def test_collect_modules(self, tmpdir: local) -> None:
        self._write_module(tmpdir)
        self._write_module(tmpdir, "setup")
        collector, _requires = await self._collect(tmpdir)
        assert collector.dist.ext.modules == {"xxx"}
        self._write_module(tmpdir, "yyy")
        collector, _requires = await self._collect(tmpdir)
        assert collector.dist.ext.modules == {"xxx", "yyy"}
