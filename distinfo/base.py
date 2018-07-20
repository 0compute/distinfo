from __future__ import annotations

import contextlib
import dataclasses
import functools
import logging
from typing import TYPE_CHECKING, cast

from . import util

if TYPE_CHECKING:
    from collections.abc import Callable, Generator
    from typing import Any

log = logging.getLogger(__package__)


# XXX: ideally we could define dataclass here as a `functools.partial` then import it
# where required but mypy's dataclasses plugin won't then see the classes as
# dataclasses, so we define the defaults here and accept a bit more boilerplate
DATACLASS_DEFAULTS = dict(
    repr=False,
    eq=False,
    # NOTE: slots messes with super(): https://stackoverflow.com/questions/73268995
    slots=True,
)


@dataclasses.dataclass(**DATACLASS_DEFAULTS)
class SelfLogger:
    obj: Base | str

    _logger: logging.Logger

    @classmethod
    def factory(cls, obj: Base | str) -> SelfLogger:
        return cls(obj=obj, _logger=logging.getLogger(type(obj).__module__))

    def _log(
        self, level: str, msg: str, *args: Any, noself: bool = False, **kwargs: Any
    ) -> None:
        kwargs.setdefault("stacklevel", 3)
        obj_repr = isinstance(self.obj, str) and self.obj or repr(self.obj)
        getattr(self._logger, level)(
            f"{'' if noself else f'{obj_repr}: '}{msg}", *args, **kwargs
        )

    def __getattr__(self, level: str) -> Callable:
        return functools.partial(self._log, level)

    @contextlib.contextmanager
    def duration(
        self, msg: str, *args: Any, **kwargs: Any
    ) -> Generator[None, None, None]:
        with util.log_duration(msg, *args, logger=cast(logging.Logger, self), **kwargs):
            yield


class Base:
    def __hash__(self) -> int:
        return hash(self.__class__.__name__ + str(self))

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, str):
            other = str(other)
        return str(self) == other

    def __repr__(self) -> str:
        name = type(self).__name__
        try:
            return f"<{name} {self}>"
        except Exception:  # pragma: no ftest ptest cover
            return f"<unprintable {name}>"

    clog = log

    @util.cached_property
    def log(self) -> SelfLogger:
        return SelfLogger.factory(obj=self)

    def replace(self, **changes: Any) -> Base:
        return dataclasses.replace(self, **changes)
