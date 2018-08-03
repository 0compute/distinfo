import importlib

from distinfo import config
from distinfo.distribution import Distribution
from distinfo.requirement import Requirement

from .cases import Case


class DummyCollector:

    def __init__(self, dist):
        self.dist = dist

    def collect(self):
        self.dist.name = "xxx"


class DummyModule:

    DummyCollector = DummyCollector


class TestDistribution(Case):

    def test_normalized_name(self):
        dist = Distribution()
        assert dist.normalized_name == "unknown"

    def test_version(self):
        dist = Distribution()
        assert dist.version == "0.0.0"
        dist.version = "1"
        assert dist.metadata.version == "1"

    def test_add_requirement(self):
        dist = Distribution()
        dist.add_requirement("xxx")
        dist.add_requirement(Requirement.from_line("xxx"))
        assert {"xxx"} == dist.requires.run
        dist.add_requirement("xxx", extra="test")
        assert {"xxx"} == dist.requires.run
        assert not dist.requires.test
        dist.add_requirement("yyy", extra="test")
        assert {"yyy"} == dist.requires.test
        dist.add_requirement("zzz; python_version > '1'", extra="build")
        assert {"zzz"} == dist.requires.build
        dist.add_requirement("zzz", extra="build:python_version > '1'")
        dist.add_requirement("aaa", extra=":python_version > '1'")
        assert {"aaa", "xxx"} == dist.requires.run
        dist.add_requirement("ccc", extra=":python_version < '1'")
        assert {"aaa", "xxx"} == dist.requires.run

    def test_add_requirement_implicit(self):
        dist = Distribution()
        dist.add_requirement("setuptools")
        assert not dist.requires

    def test_add_requirement_unnamed(self, caplog):
        dist = Distribution()
        dist.add_requirement(".")
        dist.add_requirement("-e .")
        assert not dist.requires
        assert "ignoring unnamed" in caplog.text

    def test_add_requirement_invalid(self, caplog):
        dist = Distribution()
        dist.add_requirement("-cxxx")
        assert "RequirementParseError" in caplog.text

    def test_init_dummy_collect(self, monkeypatch, tmpdir):
        monkeypatch.setitem(config.cfg, "collectors", ["DummyCollector"])
        monkeypatch.setattr(importlib, "import_module", lambda _x: DummyModule())
        self._write_setup(tmpdir)
        dist = Distribution(req=Requirement.from_line(str(tmpdir)))
        assert dist.name == "xxx"
