from __future__ import annotations

from typing import TYPE_CHECKING

from distinfo.collector import Cargo

from .cases import Case

if TYPE_CHECKING:
    from py.path import local


class TestCargo(Case):
    collector = Cargo

    async def test_collect_root(self, tmpdir: local) -> None:
        tmpdir.join("a.file").write("")
        tmpdir.join("Cargo.lock").write("")
        collector, _requires = await self._collect(tmpdir)
        assert collector.dist.ext.cargo == "."

    async def test_collect_deep(self, tmpdir: local) -> None:
        tmpdir.join("a/b/c/Cargo.lock").write("", ensure=True)
        collector, _requires = await self._collect(tmpdir)
        assert collector.dist.ext.cargo == "a/b/c"

    async def test_collect_ignored(self, tmpdir: local) -> None:
        tmpdir.join("examples/a/b/Cargo.lock").write("", ensure=True)
        collector, _requires = await self._collect(tmpdir)
        assert "cargo" not in collector.dist.ext
