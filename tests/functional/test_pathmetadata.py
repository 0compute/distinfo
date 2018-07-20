from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from distinfo.collector import PathMetadata

from .cases import Case

if TYPE_CHECKING:
    from py.path import local

PKG_INFO = """
Version: 1
"""


class TestPathMetadata(Case):
    collector = PathMetadata

    async def _assert(self, tmpdir: local) -> None:
        collector, _requires = await self._collect(tmpdir)
        assert collector.dist.version == "1"

    @pytest.mark.parametrize("path", PathMetadata.INFO_DIRS)
    async def test_collect_info_dir(self, tmpdir: local, path: str) -> None:
        tmpdir.join(f"xxx.{path}").write(PKG_INFO.strip(), ensure=True)
        await self._assert(tmpdir)

    async def test_collect_sdist(self, tmpdir: local) -> None:
        tmpdir.join("PKG-INFO").write(PKG_INFO.strip())
        await self._assert(tmpdir)
