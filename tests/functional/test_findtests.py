from __future__ import annotations

from typing import TYPE_CHECKING

from distinfo.collector import FindTests

from .cases import Case

if TYPE_CHECKING:
    from py.path import local


class TestFindTests(Case):
    collector = FindTests

    async def test_collect(self, tmpdir: local) -> None:
        self._write_module(tmpdir, "test")
        collector, _requires = await self._collect(tmpdir)
        assert collector.dist.ext.tests == {"test.py"}

    async def test_collect_empty(self, tmpdir: local) -> None:
        collector, _requires = await self._collect(tmpdir, fail=True)
        assert "tests" not in collector.dist.ext

    async def test_collect_empty_testdir(self, tmpdir: local) -> None:
        tmpdir.join("test").mkdir()
        await self.test_collect_empty(tmpdir)

    async def test_collect_excluded(self, tmpdir: local) -> None:
        self._write_package(tmpdir, "example", mod_name="test")
        self._write_module(tmpdir, "test")
        collector, _requires = await self._collect(tmpdir)
        assert collector.dist.ext.tests == {"test.py"}

    async def test_collect_test_package(self, tmpdir: local) -> None:
        self._write_package(tmpdir, "aaa")
        self._write_package(tmpdir, "test")
        collector, _requires = await self._collect(tmpdir)
        assert collector.dist.ext.tests == {"test"}

    async def test_collect_testdir(self, tmpdir: local) -> None:
        test = self._write_package(tmpdir, "test", mod_name="test")
        collector, _requires = await self._collect(tmpdir)
        assert collector.dist.ext.tests == {"test/test.py"}
        self._write_module(test, "test2")
        collector, _requires = await self._collect(tmpdir)
        assert collector.dist.ext.tests == {"test"}

    async def test_collect_no_common_prefix(self, tmpdir: local) -> None:
        self._write_package(tmpdir, "one", mod_name="test")
        self._write_package(tmpdir, "two", mod_name="test")
        collector, _requires = await self._collect(tmpdir)
        assert collector.dist.ext.tests == {"one/test.py", "two/test.py"}
