from __future__ import annotations

import dataclasses
from typing import ClassVar

import anyio

from ..base import DATACLASS_DEFAULTS
from .collector import Collector


@dataclasses.dataclass(**DATACLASS_DEFAULTS)
class Cargo(Collector):
    CARGO_LOCK: ClassVar[str] = "Cargo.lock"

    async def _collect(self) -> bool:
        for path in self.sorted_files:
            if path.endswith(self.CARGO_LOCK):
                self.dist.ext.cargo = str(anyio.Path(path).parent)
                self.log.debug(f"found Cargo.lock: {self.dist.ext.cargo}")
                break
        return True
