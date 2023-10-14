from __future__ import annotations

from typing import TYPE_CHECKING

from distinfo.collector import Cargo

from .cases import Case

if TYPE_CHECKING:
    from py.path import local


class TestCargo(Case):
    collector = Cargo

    async def test_collect_empty(self, tmpdir: local) -> None:
        collector, _requires = await self._collect(tmpdir, fail=True)
        assert "cargo" not in collector.dist.ext

    async def test_collect_ignored(self, tmpdir: local) -> None:
        tmpdir.join("examples/a/b/Cargo.lock").write("", ensure=True)
        await self.test_collect_empty(tmpdir)

    async def test_collect_root(self, tmpdir: local) -> None:
        tmpdir.join("a.file").write("")
        tmpdir.join("Cargo.lock").write("")
        collector, _requires = await self._collect(tmpdir)
        assert collector.dist.ext.cargo == "."

    async def test_collect_deep(self, tmpdir: local) -> None:
        tmpdir.join("a/b/c/Cargo.lock").write("", ensure=True)
        collector, _requires = await self._collect(tmpdir)
        assert collector.dist.ext.cargo == "a/b/c"
