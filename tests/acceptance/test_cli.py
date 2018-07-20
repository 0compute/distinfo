from __future__ import annotations

from typing import TYPE_CHECKING

import anyio
import pytest
from box import Box
from click.testing import CliRunner
from setuptools import sandbox

from distinfo import cli, const, util

from ..functional.cases import Case
from ..functional.test_pyprojectmetadata import PYPROJECT

if TYPE_CHECKING:
    from typing import Any

    from py.path import local


class TestCli(Case):
    def _assert_dist(self, dist: Box) -> None:
        assert dist.name == "xxx"
        assert dist.requires.build_system_requires == {"aaa"}
        assert dist.requires.dev == {"bbb"}

    def _invoke(
        self,
        *args: str,
        tmpdir: local,
        fmt: str = "json",
        assert_dist: bool = True,
        exit_code: int = 0,
        **kwargs: Any,
    ) -> Box:
        kwargs.setdefault("catch_exceptions", False)
        kwargs.setdefault("color", True)
        self._write_pyproject(tmpdir, PYPROJECT)
        result = CliRunner(mix_stderr=False).invoke(
            cli._main,
            (*args, "-vv", f"--format={fmt}", "--evaluate", str(tmpdir)),
            **kwargs,
        )
        assert result.exit_code == exit_code
        stdout = result.stdout_bytes if fmt == "msgpack" else result.stdout
        dist = Box(util.list_to_set(util.loads(stdout, fmt=fmt)))
        if assert_dist:
            self._assert_dist(dist)
        return dist

    def test_extract(self, tmpdir: local) -> None:
        self._invoke(tmpdir=tmpdir)

    def test_extract_set(self, tmpdir: local) -> None:
        dist = self._invoke(
            "--set=name:aaa", "--set=ext.x:1", tmpdir=tmpdir, assert_dist=False
        )
        assert dist.name == "aaa"
        assert dist.ext.x == "1"

    def test_extract_single_collector(self, tmpdir: local) -> None:
        dist = self._invoke(
            "--set=ext.build_backend:setuptools.build_meta",
            "--collector=PyProjectDynamicMetadata",
            tmpdir=tmpdir,
            assert_dist=False,
            input=util.dumps([const.PYPROJECT_TOML], fmt="msgpack"),
        )
        assert dist.name == "xxx"

    def test_extract_no_such(self) -> None:
        result = CliRunner().invoke(cli._main, ("/no/such/path",))
        assert result.exit_code == 2

    def test_extract_msgpack(self, tmpdir: local) -> None:
        self._invoke(tmpdir=tmpdir, fmt="msgpack")

    def test_extract_include_exclude(self, tmpdir: local) -> None:
        dist = self._invoke("--include=name", tmpdir=tmpdir, assert_dist=False)
        assert "name" in dist
        dist = self._invoke("--exclude=name", tmpdir=tmpdir, assert_dist=False)
        assert "name" not in dist

    def test_extract_core_metadata(self, tmpdir: local) -> None:
        dist = self._invoke("--core-metadata", tmpdir=tmpdir, assert_dist=False)
        assert dist.requires_dist == {
            "aaa; extra == 'build-system-requires'",
            "bbb; extra == 'dev'",
        }

    def test_as_module(self, tmpdir: local, capsys: pytest.CaptureFixture) -> None:
        self._write_pyproject(tmpdir, PYPROJECT)
        main = str(anyio.Path(cli.__file__).parent / "__main__.py")
        with sandbox.save_argv((main, "-fjson", str(tmpdir))):  # type: ignore[attr-defined]
            pytest.raises(
                SystemExit,
                sandbox._execfile,  # type: ignore[attr-defined]
                main,
                dict(__file__=main, __name__="__main__"),
            )
        dist = Box(util.list_to_set(util.loads(capsys.readouterr().out, fmt="json")))
        self._assert_dist(dist)
