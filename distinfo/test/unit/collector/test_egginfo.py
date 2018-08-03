from ....collectors.egginfo import EggInfo

from .cases import Case

SETUP = """
from setuptools import setup
setup(
    install_requires=["bbb"],
    extras_require=dict(test="ddd"),
)
"""


class TestEggInfo(Case):

    collector = EggInfo

    def test_collect(self, tmpdir):
        self._run_egg_info(tmpdir, SETUP)
        collector = self._collect(tmpdir)
        assert {"bbb"} == collector.requires.run
        assert {"ddd"} == collector.requires.test

    def test_collect_no_requires(self, tmpdir):
        self._run_egg_info(tmpdir)
        collector = self._collect(tmpdir)
        assert not collector.requires

    def test_collect_empty(self, caplog, tmpdir):  # pylint: disable=arguments-differ
        super().test_collect_empty(tmpdir)
        assert "has no PKG-INFO" in caplog.text
