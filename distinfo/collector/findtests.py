from __future__ import annotations

import dataclasses
import os.path
from fnmatch import fnmatch
from typing import ClassVar

from .. import const, util
from ..base import DATACLASS_DEFAULTS
from .collector import Collector


@dataclasses.dataclass(**DATACLASS_DEFAULTS)
class FindTests(Collector):
    FILE_GLOB: ClassVar[str] = "*test*.py"

    async def _collect(self) -> bool:
        tests = []
        for test_dir in const.TEST_DIR_NAMES:
            for path in sorted(self.packages, key=len):
                if path == test_dir or path.endswith(f"/{test_dir}"):
                    tests.append(path)
                    break
            if tests:
                break
        if not tests:
            tests = [
                path
                for path in self.sorted_files
                if fnmatch(path.split(os.sep)[-1], self.FILE_GLOB)
            ]
        if tests:
            prefix = os.path.commonpath(tests)
            if prefix:
                tests = [prefix.rstrip(os.sep)]
            else:  # pragma: no ftest ptest cover
                util.raise_on_hit()
            self.dist.ext.tests = set(tests)
            self.log.debug(f"found tests: {util.irepr(tests, repr=str)}")
        return True
