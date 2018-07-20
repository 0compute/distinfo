from __future__ import annotations

from typing import TYPE_CHECKING

from box import Box
from setuptools import sandbox
from setuptools.dist import Distribution as SetuptoolsDistribution

from distinfo import Requires, const
from distinfo.collector import SetuptoolsMetadata

from .cases import Case

if TYPE_CHECKING:
    import pytest
    from py.path import local

    from distinfo.collector import Collector

BARE_SETUP = "__import__('setuptools').setup()"


SETUP_PY = r"""
import sys

from setuptools import setup, find_packages

if __name__ == "__main__":
    # print some stuff to test filters
    print("some dirt")
    print("other dirt", file=sys.stderr)
    print("\n", file=sys.stderr)
    setup(
        py_modules=["yyy"],
        packages=find_packages(),
        install_requires=["eee"],
        # badly specified requirements, seen in unittest2
        tests_require="ccc",
        test_suite="xxx.yyy",
        extras_require={
            ":python_version > '1'": ["aaa"],
            "xxx:python_version > '1'": ["ddd"],
        },
        license_file="LICENSE",
        url="http://example.org",
        entry_points={
            'console_scripts': [
                'hello = yyy:hello',
            ]
        },
    )
"""

SETUP_CFG = """
[metadata]
name = a
url = http://example.org
[options]
license_file = LICENSE
py_modules = yyy
packages =
    xxx
    tests
    uuu
install_requires =
    eee
    aaa; python_version > '1'
tests_require = ccc
test_suite = xxx.yyy
[options.extras_require]
xxx = ddd
"""


class TestSetuptoolsMetadata(Case):
    collector = SetuptoolsMetadata

    def _write_bare_setup(self, tmpdir: local) -> None:
        self._write_setup(tmpdir, BARE_SETUP)

    def _assert_basic(self, collector: Collector, requires: Requires) -> None:
        assert requires.run == {"aaa", "eee"}
        assert requires.xxx == {"ddd"}
        assert requires.test == {"ccc"}
        assert collector.dist.home_page == "http://example.org"
        assert collector.dist.license == "A"
        assert collector.dist.ext.modules == {"yyy"}
        assert collector.dist.ext.packages == {"xxx"}
        assert collector.dist.ext.setuptools_test.suite == "xxx.yyy"

    def _basic_setup(self, tmpdir: local) -> None:
        self._write_package(tmpdir)
        self._write_module(tmpdir, "yyy")
        tmpdir.join("LICENSE").write("A")

    async def test_collect(self, tmpdir: local) -> None:
        self._basic_setup(tmpdir)
        self._write_setup(tmpdir, SETUP_PY)
        # basic
        collector, requires = await self._collect(tmpdir)
        assert collector.exists
        self._assert_basic(collector, requires)
        assert collector.dist.ext.entrypoints == dict(
            console_scripts=Box(hello="yyy:hello")
        )
        # exclude
        collector, requires = await self._collect(
            tmpdir, options=dict(exclude=("home_page",))
        )
        assert collector.dist.home_page is None
        # subprocess
        collector, requires = await self._collect(
            tmpdir, options=dict(modify_globals=False)
        )
        self._assert_basic(collector, requires)
        # subprocess exclude
        collector, requires = await self._collect(
            tmpdir, options=dict(modify_globals=False, exclude=("home_page",))
        )
        assert collector.dist.home_page is None

    async def test_collect_setup_cfg_only(self, tmpdir: local) -> None:
        self._basic_setup(tmpdir)
        tmpdir.join(const.SETUP_CFG).write(SETUP_CFG)
        collector, requires = await self._collect(tmpdir)
        assert collector.exists
        self._assert_basic(collector, requires)

    async def test_collect_exc(
        self,
        tmpdir: local,
        monkeypatch: pytest.MonkeyPatch,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        self._write_bare_setup(tmpdir)
        monkeypatch.setattr(sandbox, "_execfile", self._raiser(Exception))
        await self._collect(tmpdir, fail=True)
        assert "fail" in caplog.text

    async def test_collect_exc_systemexit(
        self,
        tmpdir: local,
        monkeypatch: pytest.MonkeyPatch,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        self._write_bare_setup(tmpdir)
        monkeypatch.setattr(sandbox, "_execfile", self._raiser(SystemExit, "xfail"))
        await self._collect(tmpdir, fail=True)
        assert "xfail" in caplog.text

    async def test_collect_exc_distutilssetuperror(
        self,
        tmpdir: local,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        # imported here cos setuptools patches distutils so must be first
        from distutils.errors import DistutilsSetupError

        self._write_bare_setup(tmpdir)
        monkeypatch.setattr(
            SetuptoolsDistribution,
            "_finalize_setup_keywords",
            self._raiser(DistutilsSetupError),
        )
        collector, requires = await self._collect(tmpdir)
        assert not requires
