from __future__ import annotations

import contextlib
import dataclasses
import email
from importlib.metadata import Distribution as ImportlibDistribution
from typing import TYPE_CHECKING

import anyio
from box import Box

from ... import const, util
from ...base import DATACLASS_DEFAULTS
from ..collector import Collector

if TYPE_CHECKING:
    from typing import Any


@dataclasses.dataclass(**DATACLASS_DEFAULTS)
class MetadataCollector(Collector):
    async def __call__(self) -> bool:
        await super(MetadataCollector, self).__call__()
        self.dist.ext.setdefault("collectors", Box())[type(self).__name__] = self.result
        return self.result

    async def add_requirements(self, extra: str, *reqs: str) -> None:
        # build_system_requires and get_requires_for_build may return empty strings
        if reqs := tuple(r for r in reqs if r):
            await self.dist.add_requirements(extra, *reqs)
            self.log.debug(
                f"requires[{extra or const.RUN_EXTRA}]: {util.irepr(reqs, repr=str)}"
            )

    async def update_from_pkginfo(self, pkginfo: str) -> None:
        await self.dist.update(email.message_from_string(pkginfo))

    async def update_from_importlib_metadata(self, path: anyio.Path) -> None:
        dist = ImportlibDistribution.at(path)
        metadata = Box((await anyio.to_thread.run_sync(lambda: dist.metadata)).json)
        if (
            path.suffix == ".egg-info"
            and "requires_dist" not in metadata
            and dist.requires
        ):
            metadata.requires_dist = dist.requires
        license_file = metadata.pop("license_file", None)
        # https://peps.python.org/pep-0639/
        if (
            license_expression := metadata.pop("license_expression", None)
        ) is not None:  # pragma: no ptest cover
            util.raise_on_hit()
            metadata.license = license_expression
        elif license_file is not None:
            await self._try_set_license(metadata, license_file)
        await self.dist.update(metadata)
        self.log.debug(f"update from importlib metadata: {path.name}")
        packages = {
            p
            for p in {
                # seen in httpcore
                p.strip().replace("/", ".")
                for p in (
                    await anyio.to_thread.run_sync(dist.read_text, "top_level.txt")
                    or ""
                ).split()
            }
            if p
        }
        if packages:
            await self.set_packages(packages)

    async def _try_set_license(self, obj: Any, path: str) -> None:
        # FIXME: don't suppress UnicodeDecodeError
        with contextlib.suppress(FileNotFoundError, UnicodeDecodeError):
            obj.license = await (self.path / path).read_text()
