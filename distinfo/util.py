from __future__ import annotations

import contextlib
import functools
import io
import json
import logging
import os
import sys
import tempfile
import time
from typing import TYPE_CHECKING, overload

import aiofiles
import atools
import msgpack
import yaml
from box import Box

from . import const

if TYPE_CHECKING:
    from collections.abc import Callable, Generator, Iterable
    from typing import IO, Any, Literal

    import anyio


log = logging.getLogger(__name__)


def envvar(name: str) -> str:
    return f"{const.ENVVAR_PREFIX}_{name.upper()}"


# XXX: looking for code paths not exercised by package tests to see if they can
# be safely removed
if os.environ.get(envvar("raise_on_hit")) == "1":  # pragma: no cover

    class WinnerWinnerChickenDinnerError(Exception):
        ...

    def raise_on_hit() -> None:
        raise WinnerWinnerChickenDinnerError

else:

    def raise_on_hit() -> None:  # pragma: no cover
        ...


def sorted_lc(iterable: Iterable) -> list:
    return sorted(iterable, key=lambda o: str(o).lower())


def joinmap(iterable: Iterable, func: Callable = str, sep: str = ", ") -> str:
    return sep.join(map(func, iterable))


REPR_MAX_LENGTH = 50


def trepr(
    obj: Any,
    *,
    repr: Callable = repr,  # noqa: A002
    max_length: int | None = REPR_MAX_LENGTH,
) -> str:
    """Truncated repr"""
    repr_str = repr(obj)
    if max_length is not None and len(repr_str) - 2 > max_length:
        end = ""
        match repr_str[0]:
            case "[":
                end = "]"
            case "{":
                end = "}"
            case "(" | "Box(":
                end = ")"
            case "<":
                end = ">"
            case "'":  # pragma: no branch
                end = "'"
        repr_str = f"{repr_str[:max_length]}…{end}"
    return repr_str


def irepr(
    iterable: Iterable,
    sep: str = ", ",
    repr: Callable = repr,  # noqa: A002
    max_length: int | None = REPR_MAX_LENGTH,
) -> str:
    """Iterable repr"""
    return joinmap(
        sorted_lc(iterable) if isinstance(iterable, set) else iterable,
        functools.partial(trepr, repr=repr, max_length=max_length),
        sep,
    )


@overload
def clean_dict(odict: dict) -> dict:
    ...


@overload
def clean_dict(odict: dict, *, inplace: Literal[False]) -> dict:
    ...


@overload
def clean_dict(odict: dict, *, inplace: Literal[True]) -> None:
    ...


def clean_dict(odict: dict, *, inplace: bool = False) -> dict | None:
    if not inplace:
        if isinstance(odict, Box):
            odict = odict.to_dict()
        clean = {}
    for key, value in list(odict.items()):
        if isinstance(value, dict):
            if inplace:
                clean_dict(value, inplace=True)
            else:
                value = clean_dict(value)
        elif isinstance(value, list):
            for i, lvalue in enumerate(value):
                if isinstance(lvalue, dict):
                    if inplace:
                        clean_dict(lvalue, inplace=True)
                    else:
                        lvalue = value[i] = clean_dict(lvalue)
                if not lvalue:
                    del value[i]
        keep = value or isinstance(value, int | float)
        if inplace and not keep:
            del odict[key]
        elif not inplace and keep:
            clean[key] = value
    if not inplace:
        return clean


BASE_TYPES = (float, int, str, tuple)


def dump_dict(odict: dict, *, stringify: bool = False) -> dict:
    clean = type(odict)()
    for key, value in odict.items():
        if isinstance(value, dict):
            value = dump_dict(value, stringify=stringify)
        elif isinstance(value, list | set | tuple):
            if isinstance(value, set):
                value = sorted_lc(value)
            if stringify:
                value = [
                    dump_dict(v, stringify=stringify)
                    if isinstance(v, dict)
                    else v
                    if isinstance(v, BASE_TYPES)
                    else str(v)
                    for v in value
                ]
        elif stringify and not isinstance(value, BASE_TYPES):
            value = str(value)
        clean[key] = value
    return clean


def list_to_set(odict: dict) -> dict:
    clean = type(odict)()
    # convert lists to sets from msgpack-serialized data
    for key, value in odict.items():
        if isinstance(value, dict):
            value = list_to_set(value)
        elif isinstance(value, list):  # pragma: no branch
            value = [(list_to_set(v) if isinstance(v, dict) else v) for v in value]
            # if value contains a dict then we can't convert to set as dict is not
            # hashable
            with contextlib.suppress(TypeError):
                value = set(value)
        clean[key] = value
    return clean


def _dump(
    obj: Any,
    dumper: Callable,
    *args: Any,
    stringify: bool = True,
    **kwargs: Any,
) -> bytes | str:
    if isinstance(obj, dict):  # pragma: no branch
        obj = dump_dict(clean_dict(obj), stringify=stringify)
    return dumper(obj, *args, **kwargs)


_yaml_load = functools.partial(yaml.load, Loader=yaml.CLoader)

_yaml_dump = functools.partial(yaml.dump, Dumper=yaml.CDumper, default_flow_style=False)


def _yaml_dumps(obj: Any, *args: Any, **kwargs: Any) -> str:
    stream = io.StringIO()
    _yaml_dump(obj, *args, stream=stream, **kwargs)
    return stream.getvalue()


DEFAULT_DUMPER = "yaml"

JSON_DEFAULTS = dict(default=str, indent=2, sort_keys=True)

DUMPERS = dict(
    json=functools.partial(json.dump, **JSON_DEFAULTS),
    msgpack=msgpack.pack,
    yaml=_yaml_dump,
)

LOADERS = dict(
    json=json.load,
    msgpack=msgpack.unpack,
    yaml=_yaml_load,
)

STR_DUMPERS: dict[str, Callable] = dict(
    json=functools.partial(json.dumps, **JSON_DEFAULTS),
    msgpack=msgpack.packb,
    yaml=_yaml_dumps,
)

STR_LOADERS = dict(
    json=json.loads,
    msgpack=msgpack.unpackb,
    yaml=_yaml_load,
)


def dump(
    obj: Any, file: IO = sys.stdout, fmt: str = DEFAULT_DUMPER, **kwargs: Any
) -> None:
    if hasattr(obj, "to_dict"):
        obj = obj.to_dict()
    _dump(obj, DUMPERS[fmt], file, **kwargs)


def load(file: IO = sys.stdin, fmt: str = DEFAULT_DUMPER, **kwargs: Any) -> Any:
    return LOADERS[fmt](file, **kwargs)


@overload
def dumps(obj: Any) -> str:
    ...


@overload
def dumps(obj: Any, fmt: Literal["json"] | Literal["yaml"]) -> str:
    ...


@overload
def dumps(obj: Any, fmt: Literal["msgpack"]) -> bytes:
    ...


def dumps(obj: Any, fmt: str = DEFAULT_DUMPER, **kwargs: Any) -> bytes | str:
    return _dump(obj, STR_DUMPERS[fmt], **kwargs).strip()


def loads(value: bytes | str, fmt: str = DEFAULT_DUMPER, **kwargs: Any) -> dict:
    return STR_LOADERS[fmt](value, **kwargs)


@contextlib.contextmanager
def log_duration(
    msg: str,
    end_msg: Callable | str | None = None,
    *,
    logger: logging.Logger = log,
    level: str = "debug",
    end_level: str | None = None,
    stacklevel: int = 0,
) -> Generator[None, None, None]:
    stacklevel += 2
    start = time.monotonic()
    getattr(logger, level)(msg, stacklevel=stacklevel)
    yield
    getattr(logger, end_level or level)(
        f"{end_msg() if callable(end_msg) else end_msg if end_msg is not None else msg} "
        f"in {time.monotonic() - start:.4f}s",
        stacklevel=stacklevel,
    )


TMPDIR_PREFIX = f"{const.NAME}-"


def tmpdir(
    **kwargs: Any,
) -> aiofiles.tempfile.AiofilesContextManagerTempDir:
    kwargs["prefix"] = TMPDIR_PREFIX
    return aiofiles.tempfile.TemporaryDirectory(**kwargs)


def is_tmpdir(path: anyio.Path) -> bool:
    return str(path).startswith(f"{tempfile.gettempdir()}{os.sep}{TMPDIR_PREFIX}")


# functools.cached_property is broken: https://github.com/python/cpython/issues/87634
class cached_property(property):  # noqa: N801
    def __init__(self, fget: Callable[[Any], Any]) -> None:
        super().__init__(atools.memoize(fget, keygen=lambda self: (id(self),)))

    def __delete__(self, obj: Any) -> None:
        memoized = self.fget.memoize  # type: ignore[attr-defined]
        memoized.reset_key(memoized.get_key(memoized.keygen(obj)))
