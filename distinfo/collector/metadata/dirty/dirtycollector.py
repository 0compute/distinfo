from __future__ import annotations

import dataclasses
import os
import sys
import textwrap
from typing import ClassVar

from box import Box

from .... import command, const, util
from ....base import DATACLASS_DEFAULTS
from ..metadatacollector import MetadataCollector


@dataclasses.dataclass(**DATACLASS_DEFAULTS)
class DirtyCollector(MetadataCollector):
    ENV_PASS: ClassVar[tuple[str, ...]] = (
        util.envvar("verbose"),
        "PATH",
        "PYTHONPATH",
        "DISTINFO_RAISE_ON_HIT",
    )

    async def _collect(self) -> bool:
        if self.options.modify_globals:
            return await self._collect_dirty()
        # build cmd env
        env = {key: os.environ[key] for key in self.ENV_PASS if key in os.environ}
        # add include/exclude
        for key in ("include", "exclude"):
            value = self.options.get(key)
            if value is not None:  # pragma: no branch
                env[util.envvar(key)] = " ".join(value)
        # add verbose
        verbose = self.options.get("verbose", 0)
        if verbose != 0:  # pragma: no branch
            env[util.envvar("verbose")] = str(verbose)
        # execute
        cmd = [
            sys.executable,
            "-m",
            const.NAME,
            f"--collector={type(self).__name__}",
            "--format=msgpack",
        ]
        self._subprocess_cmd_hook(cmd)
        cmd.append(self.path)
        out = await command.run(
            *cmd,
            input=util.dumps(self.sorted_files, fmt="msgpack"),
            env=env,
        )
        # load result
        metadata = Box(util.loads(out, fmt="msgpack"))
        result = metadata.ext.collectors.pop(type(self).__name__)
        for record in metadata.ext.pop("log", []):
            # whatever it was logged at we log at debug here - warnings from setup.py
            # are not interesting in this context
            self.log.debug(record["msg"], *record.get("args", []), noself=True)
        await self.dist.merge(metadata)
        return result

    async def _collect_dirty(self) -> bool:
        raise NotImplementedError

    def _subprocess_cmd_hook(self, cmd: list[str]) -> None:
        pass

    def _log_build_exc(self, exc: BaseException) -> None:
        self.log.debug(
            f"fail:\n{textwrap.indent(f'{type(exc).__name__}: {exc}', '  ')}",
            exc_info=exc,
        )
