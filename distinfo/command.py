from __future__ import annotations

import contextlib
import io
import logging
import subprocess
from subprocess import CalledProcessError
from typing import TYPE_CHECKING, overload

import anyio
from anyio.streams.text import TextReceiveStream

from . import util

if TYPE_CHECKING:
    from collections.abc import Mapping
    from typing import Any, Literal

    from anyio.abc import ByteReceiveStream

log = logging.getLogger(__name__)


# XXX: this is incomplete - only combinations in use are defined
@overload
async def run(*command: Any) -> bytes:
    ...


@overload
async def run(
    *command: Any, input: bytes, env: Mapping[str, str]  # noqa: A002
) -> bytes:
    ...


@overload
async def run(*command: Any, lines: Literal[True]) -> list[str]:
    ...


@overload
async def run(*command: Any, lines: Literal[True], cwd: anyio.Path) -> list[str]:
    ...


async def run(
    *command: Any,
    input: bytes | None = None,  # noqa: A002
    lines: bool = False,
    cwd: anyio.Path | None = None,
    env: Mapping[str, str] | None = None,
) -> bytes | list[str]:
    with util.log_duration(subprocess.list2cmdline(command), logger=log):
        if cwd is not None:
            log.debug(f"cwd: {cwd}")
        async with (
            anyio.create_task_group() as tg,
            await anyio.open_process(
                list(map(str, command)),
                stdin=subprocess.PIPE if input else subprocess.DEVNULL,
                cwd=cwd,
                env=env,
            ) as proc,
        ):
            stdout_buffer = io.BytesIO()
            tg.start_soon(_process_stdout, proc.stdout, stdout_buffer)
            stderr_lines: list[str] = []
            tg.start_soon(_process_stderr, proc.stderr, stderr_lines)
            if input:
                await proc.stdin.send(input)
                await proc.stdin.aclose()
            try:
                returncode = await proc.wait()
            except BaseException:  # pragma: no cover - error path
                with contextlib.suppress(ProcessLookupError):
                    proc.kill()
                raise
            out = stdout_buffer.getvalue()
            if returncode != 0:  # pragma: no cover - error path
                raise CalledProcessError(
                    returncode,
                    command,
                    out,
                    "\n".join(stderr_lines),
                )
            if lines:
                return out.decode().strip().splitlines()
            return out


async def _process_stdout(stream: ByteReceiveStream, buffer: io.BytesIO) -> None:
    async for chunk in stream:
        buffer.write(chunk)


async def _process_stderr(stream: ByteReceiveStream, lines: list[str]) -> None:
    async for line in TextReceiveStream(stream):
        line = line.rstrip()
        if line:  # pragma: no branch
            lines.append(line)
            log.debug(f"err: {line}")
