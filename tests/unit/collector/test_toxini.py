import sys

from tox.exception import ConfigError

from distinfo.collectors import toxini

from .cases import Case

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
    tick
    tock
setenv =
    ONE = 1
"""

REQUIREMENTS = """
# comment

aaa
"""

TOXINI_ALT = """
[tox]
envlist = xxx
[xxx]
basepython = python%d.%d
""" % (sys.version_info.major, sys.version_info.minor)

TOXINI_BAD = """
[tox]
envlist = xxx
[testenv]
basepython = xxx
"""

TOXINI_BAD_ALT = """
[tox]
envlist = py10
"""

TOXINI_NOCONFIG = """
[tox]
envlist = doc
"""


class TestRequirementsFile(Case):

    collector = toxini.ToxIni

    def test_collect(self, tmpdir):
        tmpdir.join("tox.ini").write(TOXINI)
        tmpdir.join("requirements.txt").write(REQUIREMENTS)
        collector = self._collect(tmpdir)
        assert {"aaa", "zzz"} == collector.requires.test
        assert [["tick"], ["tock"]] == collector.ext.tox.commands
        assert collector.ext.tox.env.ONE == "1"

    def _assert_empty(self, collector):
        assert "tox" not in collector.ext
        assert not collector.requires

    def test_collect_alt(self, tmpdir):
        tmpdir.join("tox.ini").write(TOXINI_ALT)
        collector = self._collect(tmpdir)
        self._assert_empty(collector)

    def test_collect_noconfig(self, tmpdir):
        tmpdir.join("tox.ini").write(TOXINI_NOCONFIG)
        collector = self._collect(tmpdir)
        self._assert_empty(collector)

    def test_collect_bad(self, tmpdir):
        tmpdir.join("tox.ini").write(TOXINI_BAD)
        collector = self._collect(tmpdir)
        self._assert_empty(collector)

    def test_collect_bad_alt(self, tmpdir):
        tmpdir.join("tox.ini").write(TOXINI_BAD_ALT)
        collector = self._collect(tmpdir)
        self._assert_empty(collector)

    def test_collect_conf_error(self, monkeypatch, tmpdir):
        monkeypatch.setattr(toxini, "parseconfig", self._raiser(ConfigError))
        tmpdir.join("tox.ini").write(TOXINI)
        collector = self._collect(tmpdir)
        self._assert_empty(collector)
