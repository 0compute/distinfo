# whitelist for vulture
# pylint: disable=pointless-statement

import distutils
import logging

from .. import Distribution, config

distutils.core._setup_stop_after

logging.root.handlers

Distribution.ext.git
Distribution.ext.hasext

config.cfg.logging.config.isatty
