from __future__ import annotations

try:
    import tomllib
except ImportError:  # pragma: no cover
    import tomli as tomllib  # type: ignore[no-redef]

import dataclasses
from typing import ClassVar

import anyio
from box import Box
from packaging.version import Version
from pyproject_metadata import ConfigurationError, StandardMetadata

from ... import const, util
from ...base import DATACLASS_DEFAULTS
from .metadatacollector import MetadataCollector


@dataclasses.dataclass(**DATACLASS_DEFAULTS)
class PyProjectMetadata(MetadataCollector):
    TABLE_KEYS: ClassVar[tuple[str, str]] = ("license", "readme")

    @util.cached_property
    def exists(self) -> bool:
        # XXX: see `SetuptoolsMetadata.exists`
        exists = const.PYPROJECT_TOML in self.files
        self.log.spam(f"exists: {exists}")
        return exists

    async def _collect(self) -> bool:
        try:
            pyproject = Box(
                tomllib.loads(await (self.path / const.PYPROJECT_TOML).read_text())
            )
        except tomllib.TOMLDecodeError as exc:  # pragma: no ptest cover
            util.raise_on_hit()
            self.log.debug(f"toml parse fail: {exc}")
            return False

        # PEP 518 metadata
        # https://peps.python.org/pep-0518/#build-system-table
        if (build_system := pyproject.get("build-system")) is None:
            self.log.debug("build-system missing")
            return await self._set_default_build_system_requires()

        if (reqs := build_system.get("requires")) is None:  # pragma: no ptest cover
            util.raise_on_hit()
            self.log.debug("build-system.requires missing")
            return await self._set_default_build_system_requires()
        await self.add_requirements(const.BUILD_SYSTEM_EXTRA, *reqs)

        # PEP 517 metadata
        # https://peps.python.org/pep-0517/#source-trees
        if (build_backend := build_system.get("build-backend")) is None:
            self.log.debug("build-system.build-backend missing")
            return False
        self.dist.ext.build_backend = build_backend

        # if we got this far then we have enough for a PEP 517 build
        self.dist.ext.format = "pyproject"

        # PEP 621 metadata
        if (project := pyproject.get("project")) is None:
            self.log.debug("project missing")
            return False

        # drop table keys if excluded to avoid needless io
        for key in self.TABLE_KEYS:
            if key in project and self.dist._excluded(
                key
            ):  # pragma: no ftest ptest cover
                del project[key]

        # keep dynamic cos StandardMetadata messes with it
        dynamic = {
            # filter already set and excluded from dynamic so PyProjectDymanicMetadata
            # is not run needlessly
            key
            for key in project.get("dynamic", [])
            if key not in self.dist._init_keys and not self.dist._excluded(key)
        }

        while True:
            try:
                metadata = await anyio.to_thread.run_sync(
                    StandardMetadata.from_pyproject, pyproject
                )
            except ConfigurationError as exc:
                # error on key: delete it
                self.log.debug(f"{const.PYPROJECT_TOML} error: {exc}")
                if exc.key is None:  # pragma: no ptest cover
                    util.raise_on_hit()
                    return False
                # key as "project.{key}[.{subkey}]"
                parts = exc.key.split(".")
                del project[parts[1]]
            else:
                break

        # update dist
        if not metadata.version:
            # StandardMetadata.as_rfc822 requires version to be set, if "version" is in
            # dynamic it raises ConfigurationError
            metadata.version = Version(self.dist.version or const.NULL_VERSION)
        await self.update_from_pkginfo(str(metadata.as_rfc822()))

        # we want dynamic unaltered, dynamic version is allowed by the spec, used by
        # flit-core
        if dynamic:
            self.log.debug(f"dynamic: {util.irepr(dynamic)}")
            await self.dist.update(dynamic=dynamic)

        # add extended metadata
        for key in ("entrypoints", "scripts", "gui_scripts"):
            value = getattr(metadata, key)
            if value:
                self.dist.ext[key] = value

        # add setuptools where
        packages = pyproject.get("tool", {}).get("setuptools", {}).get("packages")
        if (
            isinstance(packages, dict)
            and (where := packages.get("find", {}).get("where")) is not None
        ):
            self.dist.ext.where = where

        return True

    async def _set_default_build_system_requires(self) -> bool:
        await self.add_requirements(
            const.BUILD_SYSTEM_EXTRA, *const.DEFAULT_BUILD_SYSTEM_REQUIRES
        )
        return False
