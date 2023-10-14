from __future__ import annotations


def capnames(*names: str) -> tuple[str, ...]:
    return (*names, *[name.capitalize() for name in names])


# used by clients with as part of a cache key, must be incremented on any fundamental
# change
SERIAL = 1

NAME = __package__

VERSION = "0.3.0.dev0"

ENVVAR_PREFIX = NAME.upper()

NULL_VALUE = "UNKNOWN"

NULL_VERSION = "0.0.0"

PYPROJECT_TOML = "pyproject.toml"

SETUP_CFG = "setup.cfg"

SETUP_PY = "setup.py"

BUILD_SYSTEM_EXTRA = "build-system-requires"

RUN_EXTRA = "run"

TEST_EXTRA = "test"

# https://peps.python.org/pep-0518/#build-system-table
DEFAULT_BUILD_SYSTEM_REQUIRES = ("setuptools", "wheel")

IGNORE_DIR_NAMES = capnames(
    "doc", "example", "examples", "samples", "vendor", "vendored"
)

TEST_DIR_NAMES = capnames("test", "tests", "testing", "unittests")
