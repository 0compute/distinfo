from __future__ import annotations

from typing import TYPE_CHECKING

from distinfo import const
from distinfo.collector import PyProjectMetadata

from .cases import Case

if TYPE_CHECKING:
    import pytest
    from py.path import local

BUILD_SYSTEM = """
[build-system]
requires = ["aaa"]
build-backend = "aaa"
"""

SETUPTOOLS_BUILD_SYSTEM = """
[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"
"""


PYPROJECT = f"""
{BUILD_SYSTEM}

[project]
name = "xxx"
version = "1"
authors = [{{name = "one", email = "one@0example.com"}}]
requires-python = ">=3.7"
classifiers = [
    "Programming Language :: Rust",
    "Programming Language :: Python :: Implementation :: CPython",
    "Programming Language :: Python :: Implementation :: PyPy",
]
readme = "yyy"

[project.license]
text = "gpl"

[project.optional-dependencies]
dev = ["bbb"]
"""

PYPROJECT_NO_BUILD_SYSTEM_REQUIRES = """
[build-system]
build-backend = "aaa"
"""

PYPROJECT_NO_BUILD_SYSTEM_BACKEND = """
[build-system]
requires = ["aaa"]
"""

PYPROJECT_CONFIG_ERROR = f"""
{BUILD_SYSTEM}

[project]
name = "xxx"
version = "1"
description = 1
"""

PYPROJECT_CONFIG_ERROR_DYNAMIC = f"""
{BUILD_SYSTEM}

[project]
dynamic = ["name"]
"""


class TestPyProjectMetadata(Case):
    collector = PyProjectMetadata

    async def test_collect(self, tmpdir: local) -> None:
        self._write_pyproject(tmpdir, PYPROJECT)
        collector = await self._mk_collector(
            tmpdir, options=dict(exclude=("description",))
        )
        assert collector.exists
        _collector, requires = await self._collect(tmpdir, collector)
        assert _collector == collector
        assert "run" not in requires
        assert requires.build_system_requires == {"aaa"}
        assert requires.dev == {"bbb"}
        assert collector.dist.name == "xxx"
        assert collector.dist.license == "gpl"
        assert collector.dist.description is None

    async def test_collect_parse_error(
        self, tmpdir: local, caplog: pytest.LogCaptureFixture
    ) -> None:
        self._write_pyproject(tmpdir, "xxx")
        await self._collect(tmpdir, fail=True)
        assert "toml parse fail" in caplog.text

    async def test_collect_no_build_system(
        self, tmpdir: local, caplog: pytest.LogCaptureFixture
    ) -> None:
        self._write_pyproject(tmpdir, "")
        await self._collect(tmpdir, fail=True)
        assert "build-system missing" in caplog.text

    async def test_collect_no_build_system_requires(
        self, tmpdir: local, caplog: pytest.LogCaptureFixture
    ) -> None:
        self._write_pyproject(tmpdir, PYPROJECT_NO_BUILD_SYSTEM_REQUIRES)
        await self._collect(tmpdir, fail=True)
        assert "build-system.requires missing" in caplog.text

    async def test_collect_no_build_system_backend(
        self, tmpdir: local, caplog: pytest.LogCaptureFixture
    ) -> None:
        self._write_pyproject(tmpdir, PYPROJECT_NO_BUILD_SYSTEM_BACKEND)
        await self._collect(tmpdir, fail=True)
        assert "build-system.build-backend missing" in caplog.text

    async def test_collect_no_project(
        self, tmpdir: local, caplog: pytest.LogCaptureFixture
    ) -> None:
        self._write_pyproject(tmpdir, BUILD_SYSTEM)
        await self._collect(tmpdir, fail=True)
        assert "project missing" in caplog.text
        self._write_pyproject(tmpdir, SETUPTOOLS_BUILD_SYSTEM)
        collector, _requires = await self._collect(tmpdir, fail=True)
        assert "project missing" in caplog.text
        assert not collector.dist.dynamic

    async def test_collect_configerror(
        self, tmpdir: local, caplog: pytest.LogCaptureFixture
    ) -> None:
        self._write_pyproject(tmpdir, PYPROJECT_CONFIG_ERROR)
        await self._collect(tmpdir)
        assert f"{const.PYPROJECT_TOML} error" in caplog.text

    async def test_collect_configerror_dynamic(
        self, tmpdir: local, caplog: pytest.LogCaptureFixture
    ) -> None:
        self._write_pyproject(tmpdir, PYPROJECT_CONFIG_ERROR_DYNAMIC)
        await self._collect(tmpdir, fail=True)
        assert f"{const.PYPROJECT_TOML} error" in caplog.text
