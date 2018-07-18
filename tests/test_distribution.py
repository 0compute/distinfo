from setuptools import sandbox

import pytest

from distinfo.distribution import Distribution
from distinfo.exc import DistInfoException

from .cases import TestCase


class TestDistribution(TestCase):

    def dist(self, name):
        return Distribution.from_source(self.data_path / name)

    def test_repr(self):
        dist = Distribution()
        assert "Distribution" in repr(dist)

    def test_add_requirement(self):
        dist = Distribution()
        dist.add_requirement("xxx")
        assert {"xxx"} == dist.requires_dist
        assert {"xxx"} == dist.depends.run
        assert not dist.depends.test

    def test_bad_requirement(self):
        dist = Distribution()
        dist.add_requirement("xxx")
        dist.add_requirement("-cxxx")
        assert {"xxx"} == dist.reqs

    def test_dep_map(self):
        dist = Distribution(requires_dist=["xxx"])
        assert {"xxx"} == dist._dep_map[None]  # pylint: disable=protected-access

    def test_bad_setup(self, monkeypatch):
        # pylint: disable=protected-access
        name = "test.dist"
        original = sandbox._execfile

        def _execfile(*_a, **_kw):
            raise BaseException("xxx")
        monkeypatch.setattr(sandbox, "_execfile", _execfile)
        pytest.raises(DistInfoException, self.dist, name)

        def _execfile(*a, **kw):
            original(*a, *kw)
            raise BaseException("xxx")
        monkeypatch.setattr(sandbox, "_execfile", _execfile)
        self.dist(name)
