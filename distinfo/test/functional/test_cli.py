import json
from pathlib import Path

import appdirs

from click.testing import CliRunner

import pytest

from setuptools import sandbox

from ... import cli

from .cases import Case

SETUP = """
from setuptools import setup
setup(
    name="test.dist",
    install_requires=["xxx"],
)
"""


class TestCli(Case):

    def _invoke(self, tmpdir, *args, **kwargs):
        self._run_egg_info(tmpdir, SETUP)
        exit_code = kwargs.pop("exit_code", 0)
        kwargs.setdefault("catch_exceptions", False)
        runner = CliRunner()
        result = runner.invoke(cli.main, map(str, args + (tmpdir,)), **kwargs)
        assert result.exit_code == exit_code
        return result

    def test_extract(self, tmpdir):
        result = self._invoke(tmpdir, "-c")
        print(result.output)
        # FIXME: logging writes to stdout
        # dist = json.loads(result.output)
        # assert dist["name"] == "test.dist"
        assert "test.dist" in result.output

    def test_extract_write(self, tmpdir):
        out = tmpdir.join("out.json")
        self._invoke(tmpdir, "-p", "-o", out)
        dist = json.load(open(out))
        assert dist["name"] == "test.dist"

    def test_extract_write_include_exclude(self, tmpdir):
        out = tmpdir.join("out.json")
        self._invoke(tmpdir, "-o", out, "--include=name", "--exclude=name")
        dist = json.load(open(out))
        assert not dist

    def test_requires(self, tmpdir):
        result = self._invoke(tmpdir, "-r")
        print(result.output)
        # dist = json.loads(result.output)
        # assert dist["name"] == "test.dist"
        assert "xxx" in result.output

    def test_extra(self, tmpdir):
        result = self._invoke(tmpdir, "--extra=xxx:yyy")
        print(result.output)
        # dist = json.loads(result.output)
        # assert dist["name"] == "test.dist"
        assert "yyy; extra == 'xxx'" in result.output

    def test_interactive(self, monkeypatch, tmpdir):
        monkeypatch.setattr(cli.repl, "embed", lambda *_a, **_k: True)
        monkeypatch.setattr(appdirs, "user_cache_dir", lambda *_a: tmpdir.mkdir("cache"))
        self._invoke(tmpdir.mkdir("src"), "-i")

    def test_as_module(self, tmpdir, capsys):
        self._run_egg_info(tmpdir, SETUP)
        main = str(Path(cli.__file__).parent / "__main__.py")
        with sandbox.save_argv((main, str(tmpdir))):
            pytest.raises(
                SystemExit,
                sandbox._execfile,
                main,
                dict(__file__=main, __name__="__main__"),
            )
        captured = capsys.readouterr()
        # dist = json.loads(captured.out)
        # assert dist["name"] == "test.dist"
        assert "test.dist" in captured.out
