from __future__ import annotations

import copy
import dataclasses
import urllib.parse
from typing import TYPE_CHECKING

from packaging._parser import parse_requirement
from packaging._tokenizer import ParserSyntaxError
from packaging.markers import Variable
from packaging.requirements import (
    InvalidRequirement,
    Requirement as PackagingRequirement,
)
from packaging.specifiers import SpecifierSet
from packaging.utils import canonicalize_name

from .base import DATACLASS_DEFAULTS, Base
from .marker import Marker

if TYPE_CHECKING:
    from typing import Any


@dataclasses.dataclass(**DATACLASS_DEFAULTS)
class BaseRequirement:
    name: str

    name_base: str

    extras: set[str]

    specifier: SpecifierSet

    marker: Marker | None = None

    url: str | None = None

    @property
    def pinned(self) -> bool:
        return (
            len(self.specifier._specs) == 1
            and list(self.specifier._specs)[0].operator == "=="
        )

    @classmethod
    def factory(cls, reqstr: str, **kwargs: Any) -> BaseRequirement:
        # copied from PackagingRequirement.__init__ so we can use a slotted dataclass
        try:
            parsed = parse_requirement(reqstr)
        except ParserSyntaxError as e:
            raise InvalidRequirement(str(e)) from e
        if parsed.url:
            if (url := urllib.parse.urlparse(parsed.url)).scheme == "file":
                if urllib.parse.urlunparse(url) != parsed.url:
                    raise InvalidRequirement("Invalid URL given")
            elif not (url.scheme and url.netloc) or (not url.scheme and not url.netloc):
                raise InvalidRequirement(f"Invalid URL: {parsed.url}")
            kwargs["url"] = url.geturl()
        if (markers := parsed.marker) is not None:
            # HACK: collapse unnecessary group
            if (
                len(markers) >= 3
                and isinstance(markers[0], list)
                and len(markers[0]) == 3
                and markers[0][1] == "and"
                and markers[1] == "and"
                and isinstance(markers[2][0], Variable)
                and markers[2][0].value == "extra"
            ):
                for marker in reversed(markers.pop(0)):
                    markers.insert(0, marker)
            kwargs["marker"] = Marker.factory(markers)
        return cls(
            name=canonicalize_name(parsed.name),
            name_base=parsed.name,
            extras=set(map(canonicalize_name, parsed.extras) if parsed.extras else []),
            specifier=SpecifierSet(parsed.specifier),
            **kwargs,
        )

    def __str__(self) -> str:
        # for convenience only on copy/paste, matters not
        return PackagingRequirement.__str__(self).replace('"', "'")

    def __lt__(self, other: BaseRequirement) -> bool:
        return str(self) < str(other)

    def __iand__(self, req: BaseRequirement) -> BaseRequirement:
        if req.name != self.name:
            raise ValueError(f"{self!r} & {req!r} don't work")
        if req.url is not None:
            # can't exactly merge this so we replace
            self.url = req.url
        self.extras |= req.extras
        self.specifier &= req.specifier
        if req.marker:
            if self.marker is None:
                self.marker = req.marker
            elif self.marker != req.marker:
                self.marker &= req.marker
        return self

    def __and__(self, req: BaseRequirement) -> BaseRequirement:
        return self.__class__.__iand__(copy.copy(self), req)


@dataclasses.dataclass(**DATACLASS_DEFAULTS)
class Requirement(Base, BaseRequirement):
    ...
