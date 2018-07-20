from __future__ import annotations

# monkey must come first as it does some patching, hence the name...
from . import monkey
from .collector import DistCollector
from .const import SERIAL
from .distribution import BaseDistribution, Distribution
from .requirement import BaseRequirement, Requirement
from .requires import Requires
from .util import dump, dumps, load, loads

from_path = DistCollector.from_path

del monkey
