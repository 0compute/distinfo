import pytest

from .. import config


@pytest.fixture(autouse=True)
def logging():
    config.cfg.logging.config.isatty = True
    config.configure_logging()
