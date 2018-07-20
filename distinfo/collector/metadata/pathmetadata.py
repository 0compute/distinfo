from __future__ import annotations

import dataclasses
from typing import ClassVar

from ... import const
from ...base import DATACLASS_DEFAULTS
from .metadatacollector import MetadataCollector


@dataclasses.dataclass(**DATACLASS_DEFAULTS)
class PathMetadata(MetadataCollector):
    INFO_DIRS: ClassVar[list[str]] = [
        f".{info}-info/{file}"
        for info, file in dict(dist="METADATA", egg="PKG-INFO").items()
    ]

    IGNORE_DIRS: ClassVar[tuple[str, ...]] = (
        *const.IGNORE_DIR_NAMES,
        *const.TEST_DIR_NAMES,
    )

    async def _collect(self) -> bool:
        # metadata from *.(dist|egg).info dirs or top-level PKG-INFO from sdist
        path = self.path
        for info in self.INFO_DIRS:
            for file in self.sorted_files:
                for directory in self.IGNORE_DIRS:
                    if f"{directory}/" in file:
                        break
                else:
                    if file.endswith(info):
                        # take the first found
                        path = (self.path / file).parent
                        break
            if path != self.path:
                break
        if path != self.path or "PKG-INFO" in self.files:
            await self.update_from_importlib_metadata(path)
            return True
        return False
