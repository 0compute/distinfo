from __future__ import annotations

import logging
import math
import os
import time
from logging.handlers import BufferingHandler

import anyio
import coloredlogs
from box import Box

from . import util

COLOR_DEFAULT = "auto"

COLOR_CHOICES = (COLOR_DEFAULT, "always", "never")


async def configure(
    *,
    debug: bool = False,
    verbosity: int = 0,
    buffer: bool = False,
    color: str = COLOR_DEFAULT,
) -> BufferingHandler | None:
    # as it says
    logging.captureWarnings(capture=True)
    # read config
    cfg = Box(
        util.loads(await (anyio.Path(__file__).parent / "logconfig.yaml").read_text())
    )
    # debug mode
    debug_fmt = cfg.config.pop("debug_fmt")
    if debug:  # pragma: no cover
        cfg.config.fmt = debug_fmt
        cfg.loggers["asyncio"] = "notset"
        verbosity = 3
    # set level from verbosity
    match verbosity:  # pragma: no cover
        case 0:
            cfg.config.level = "info"
        case 1:
            cfg.config.level = "verbose"
        case 2:
            cfg.config.level = "debug"
        case _:
            cfg.config.level = "spam"
    # set individual logger levels
    logging.root.setLevel(getattr(logging, cfg.config.level.upper()))
    for logger, level in cfg.loggers.items():
        logging.getLogger(logger).setLevel(getattr(logging, level.upper()))
    # option: buffering handler
    if buffer:
        handler = BufferingHandler(capacity=math.inf)  # type: ignore[arg-type]
        logging.root.handlers = [handler]
        return handler
    # NO_COLOR: see https://no-color.org/
    cfg.config.isatty = (
        None if "NO_COLOR" in os.environ or color == "auto" else color == "always"
    )
    coloredlogs.install(**cfg.config)
    # reset start time so we don't count imports
    logging._startTime = time.time()  # type: ignore[attr-defined]
