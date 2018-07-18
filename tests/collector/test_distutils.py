from distinfo.collectors import Distutils

from .cases import TestCase

SETUP = """
from setuptools import setup
setup(
    setup_requires=["setuptools"],
    install_requires=["bbb"],
    tests_require=["ccc"],
    extras_require=dict(test="ddd"),
)
"""


class TestDistutils(TestCase):

    collector = Distutils

    def test_collect(self, tmpdir):
        tmpdir.join("setup.py").write(SETUP)
        dist = self._collect(tmpdir)
        assert {"setuptools"} == dist.requires.build
        assert {"bbb"} == dist.requires.run
        assert {"ccc", "ddd"} == dist.requires.test
