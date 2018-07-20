# ruff: noqa: E402

from __future__ import annotations

# install verboselogs before importing anything else as it patches logging.getLogger
import verboselogs

verboselogs.install()


# patch setuptools on demand only because its an expensive import, importing setuptools
# has the side-effect of hacking in a patched distutils
def patch_setuptools() -> None:  # pragma: no utest cover
    import logging

    from setuptools import discovery

    # give setuptools.discovery its own logger so level can be set and don't let it log.warn
    if (
        not isinstance(discovery.log, logging.Logger)
        or discovery.log.name != discovery.__name__
    ):
        discovery.log = logging.getLogger(discovery.__name__)  # type: ignore[assignment]
        discovery.log.warn = discovery.log.debug  # type: ignore[method-assign]


# FIXME: set tempfile.tempdir directly since tempfile._get_default_tempdir fails under
# high concurrency
import os
import tempfile

tempdir = os.getenv("TMPDIR")
if tempdir is not None:
    tempfile.tempdir = tempdir
