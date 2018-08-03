from setuptools import sandbox

from .. import const

SETUP = """
from setuptools import setup
setup()
"""


class Case:

    def _raiser(self, exc=Exception):
        def _raiser(*_args, **_kwargs):
            raise exc()
        return _raiser

    def _write_setup(self, tmpdir, setup=SETUP):
        setup_py = tmpdir.join(const.SETUP_PY)
        setup_py.write(setup)
        return setup_py

    def _run_egg_info(self, *args, **kwargs):
        setup = self._write_setup(*args, **kwargs)
        sandbox.run_setup(str(setup), ["egg_info"])
