from __future__ import annotations

import functools

from .cargo import Cargo
from .collector import Collector, CollectorMixin
from .distcollector import DistCollector
from .findpackages import FindPackages
from .findtests import FindTests
from .metadata import (
    DirtyCollector,
    MetadataCollector,
    PathMetadata,
    PyProjectDynamicMetadata,
    PyProjectMetadata,
    SetuptoolsMetadata,
)
