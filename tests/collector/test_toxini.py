from tox.exception import ConfigError

from distinfo.collectors import toxini

from .cases import TestCase

TOXINI = """
[tox]
envlist = py27, pypy, py34, py35, py36, py37

[testenv]
deps =
    zzz
    -r requirements.txt
    -r requirements-missing.txt
    -c xxx
commands =
    pip install xxx
    python -m pytest
    - false
setenv =
    ONE = 1
"""

TOXINI_BAD = """
[tox]
envlist = xxx
"""


class TestRequirementsFile(TestCase):

    collector = toxini.ToxIni

    def test_collect(self, tmpdir):
        tmpdir.join("tox.ini").write(TOXINI)
        tmpdir.join("requirements.txt").write("aaa")
        dist = self._collect(tmpdir)
        assert {"aaa", "xxx", "zzz"} == dist.requires.test
        assert ["python -m pytest", "false || true"] == dist.ext.tox.commands
        assert dist.ext.tox.setenv.ONE == "1"

    def test_collect_bad(self, tmpdir):
        tmpdir.join("tox.ini").write(TOXINI_BAD)
        dist = self._collect(tmpdir)
        assert not dist.requires

    def test_collect_error(self, monkeypatch, tmpdir):
        monkeypatch.setattr(toxini, "parseconfig", self._make_raiser(ConfigError))
        tmpdir.join("tox.ini").write(TOXINI)
        dist = self._collect(tmpdir)
        assert not dist.requires
