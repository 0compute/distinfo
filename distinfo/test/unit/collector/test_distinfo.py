from .... import const
from ....collectors import distinfo

from .cases import Case

SETUP = """
from setuptools import setup, find_packages
setup(
    packages=find_packages(),
    py_modules=["yyy"],
    # setuptools will attempt to fetch setup_requires packages if not present
    # so we use one from our own requirements that is already here
    setup_requires=["appdirs"],
    install_requires=["bbb"],
    # badly specified requirements, seen in unittest2
    tests_require=(["ccc"],),
    extras_require=dict(
        test=["ddd"],
    ),
)
"""


class TestDistInfo(Case):

    collector = distinfo.DistInfo

    def test_collect(self, tmpdir):
        self._write_setup(tmpdir, SETUP)
        tmpdir.join("xxx").mkdir().join("__init__.py").write("")
        collector = self._collect(tmpdir)
        assert {"appdirs"} == collector.requires.build
        assert {"bbb"} == collector.requires.run
        assert {"ccc", "ddd"} == collector.requires.test
        assert {"xxx"} == collector.ext.packages
        assert {"yyy"} == collector.ext.modules

    def test_collect_empty(self, caplog, tmpdir):  # pylint: disable=arguments-differ
        super().test_collect_empty(tmpdir)
        assert "has no %s" % const.SETUP_PY in caplog.text
