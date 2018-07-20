from __future__ import annotations

import sys
import traceback
from types import TracebackType

import anyio
import click
from box import Box

from . import const, logconfig, util
from .collector import DistCollector


def main() -> None:
    _main(auto_envvar_prefix=const.ENVVAR_PREFIX)


@click.command(context_settings=dict(show_default=True))
@click.argument(
    "path",
    default=".",
    type=click.Path(exists=True, path_type=anyio.Path),
)
@click.option(
    "--evaluate",
    is_flag=True,
    help="Evaluate requirements.",
)
@click.option(
    "-c",
    "--core-metadata",
    is_flag=True,
    help="Output as core metadata.",
)
@click.option(
    "-f",
    "--format",
    type=click.Choice(util.DUMPERS),
    default=util.DEFAULT_DUMPER,
    help="Output format.",
)
@click.option(
    "-i", "--include", multiple=True, help="Include metadata key. Multiple supported."
)
@click.option(
    "-e", "--exclude", multiple=True, help="Exclude metadata key. Multiple supported."
)
@click.option(
    "-s",
    "--set",
    multiple=True,
    help="Set metadata key as key:value. Multiple supported.",
)
@click.option(
    "-v",
    "--verbose",
    count=True,
    show_default=False,
    help="Log verbosity, more is more.",
)
@click.option(
    "--color",
    default=logconfig.COLOR_DEFAULT,
    type=click.Choice(logconfig.COLOR_CHOICES),
    show_choices=True,
    help="Log color.",
)
# private option used by dirty collectors to call themselves in a subprocess
@click.option("--collector", hidden=True)
# developer options
@click.option("-d", "--debug", is_flag=True, hidden=True)
@click.option("-p", "--pdb", is_flag=True, hidden=True)
# if modify_globals is False dirty collectors will be run in a subprocess, the cli
# is run one-shot so it doesn't matter that it modifies globals
@click.option("-g", "--modify-globals", is_flag=True, default=True, hidden=True)
@click.version_option(const.VERSION, "--version")
@click.help_option("-h", "--help")
def _main(path: click.Path, **params: dict) -> None:
    """Extract metadata from Python source and binary distributions"""
    options = Box(params)
    anyio.run(
        _async_main,
        path,
        options,
        backend_options=dict(debug=options.debug),
    )


async def _async_main(path: click.Path, options: Box) -> None:
    try:
        # configure logging
        log_buffer = await logconfig.configure(
            debug=options.debug,
            verbosity=options.verbose,
            buffer=options.collector is not None,
            color=options.color,
        )

        # Distribution kwargs
        kwargs = dict(
            options={
                k: v for k, v in options.items() if k in DistCollector.DEFAULT_OPTIONS
            }
        )
        # update kwargs from --set params
        for value in options.pop("set"):
            option, value = value.split(":")
            if value.startswith("@"):
                value = value[1:].split(",")
            parts = option.split(".")
            key = parts.pop()
            attr = {key: value}
            while parts:
                key = parts.pop()
                attr = {key: attr}
            kwargs.update(attr)

        # run all collectors
        if options.collector is None:
            dist = await DistCollector.from_path(path, **kwargs)

        # run single collector
        else:
            dist = await DistCollector.from_dir(
                path,
                files=util.load(sys.stdin.buffer, fmt="msgpack"),
                collector=options.collector,
                **kwargs,
            )
            dist.ext.log = [
                {
                    # args may be objects so replace with repr
                    k: [
                        traceback.format_tb(v)
                        if isinstance(v, TracebackType)
                        else repr(v)
                        for v in v
                    ]
                    if k in ("args", "exc_info") and v is not None
                    else v
                    for k, v in record.__dict__.items()
                }
                for record in log_buffer.buffer
            ]

        # dump to stdout
        util.dump(
            dist.to_dict(core_metadata=options.core_metadata),
            # msgpack writes bytes so needs a buffer
            file=sys.stdout.buffer if options.format == "msgpack" else sys.stdout,
            fmt=options.format,
        )

    # pdb post-mortem
    except (Exception, anyio.ExceptionGroup) as exc:  # pragma: no cover
        if not options.pdb:
            raise
        print(exc, file=sys.stderr)
        __import__("pdb").post_mortem(exc.__traceback__)
