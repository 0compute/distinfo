from __future__ import annotations

import contextlib
import dataclasses
import importlib
from typing import TYPE_CHECKING

import anyio

from .... import util
from ....base import DATACLASS_DEFAULTS
from .dirtycollector import DirtyCollector

if TYPE_CHECKING:
    from types import ModuleType


@dataclasses.dataclass(**DATACLASS_DEFAULTS)
class PyProjectDynamicMetadata(DirtyCollector):
    # NOTE: this modifies global state by changing directory

    async def _collect_dirty(self) -> bool:
        with contextlib.chdir(self.path):
            async with util.tmpdir() as tmpdir:
                try:
                    metadata_path = await anyio.to_thread.run_sync(
                        self._backend.prepare_metadata_for_build_wheel, tmpdir
                    )
                except Exception as exc:
                    self._log_build_exc(exc)
                    return False
                else:
                    await self.update_from_importlib_metadata(
                        anyio.Path(tmpdir) / metadata_path
                    )
                    return True

    def _subprocess_cmd_hook(self, cmd: list[str]) -> None:
        cmd.extend(("--set", f"ext.build_backend:{self.dist.ext.build_backend}"))

    @util.cached_property
    def _backend(self) -> ModuleType:
        if "build_backend" not in self.dist.ext:  # pragma: no cover
            raise RuntimeError("self.dist.ext.build_backend not set")
        parts = self.dist.ext.build_backend.split(":")
        backend = importlib.import_module(parts.pop(0))
        if parts:  # pragma: no ftest ptest cover
            util.raise_on_hit()
            backend = getattr(self._backend, parts[0])
        self.log.debug(f"build-backend: {backend!r}")
        return backend
