from __future__ import annotations

import copy
import dataclasses
from typing import TYPE_CHECKING

from packaging.markers import (
    Marker as _Marker,
    Op,
    Value,
    Variable,
    _evaluate_markers,
    _format_marker,
)
from packaging.utils import canonicalize_name

from .base import DATACLASS_DEFAULTS, Base

if TYPE_CHECKING:
    from packaging._parser import MarkerItem, MarkerVar

AND_OR = ("and", "or")


@dataclasses.dataclass(**DATACLASS_DEFAULTS)
class BaseMarker(_Marker):
    _markers: list[MarkerItem]

    extras: set[str]

    @classmethod
    def factory(cls, markers: list[MarkerItem]) -> BaseMarker:
        extras = set()
        markers = markers[:]
        filtered_markers: list[MarkerItem] = []
        while markers:
            marker = markers.pop(0)
            if isinstance(marker, list) and len(marker) == 1:
                marker = marker[0]
            if (
                isinstance(marker, tuple)
                and len(marker) == 3
                and (extra := cls._get_extra(*marker)) is not None
            ):
                extras.add(canonicalize_name(extra))
                if filtered_markers and filtered_markers[-1] in AND_OR:
                    filtered_markers.pop()
                elif markers and markers[0] in AND_OR:
                    markers.pop(0)
            else:
                filtered_markers.append(marker)
        return cls(filtered_markers, extras)

    @staticmethod
    def _get_extra(lhs: MarkerVar, _op: Op, rhs: MarkerVar) -> str | None:
        if isinstance(lhs, Variable) and lhs.value == "extra":
            return rhs.value
        if isinstance(rhs, Variable) and rhs.value == "extra":
            return lhs.value

    def __str__(self) -> str:
        markers = self._markers.copy()
        if self.extras:
            extras: list[tuple | str] = []
            for i, extra in enumerate(self.extras):
                if i > 0:
                    extras.append("or")
                extras.append((Variable("extra"), Op("=="), Value(extra)))
            if markers:
                markers = [extras if len(extras) > 1 else extras[0], "and", *markers]
            else:
                markers = extras
        return _format_marker(markers)

    def __bool__(self) -> bool:
        return bool(self._markers) or bool(self.extras)

    def __iand__(self, marker: Marker) -> BaseMarker:
        if not self._markers:
            self._markers = marker._markers
        elif marker:
            self._markers.extend(("and", marker._markers))
        self.extras |= marker.extras
        return self

    def __and__(self, marker: Marker) -> BaseMarker:
        return self.__class__.__iand__(copy.copy(self), marker)

    def evaluate(
        self,
        environment: dict[str, str],
    ) -> bool:
        return _evaluate_markers(self._markers, environment)


@dataclasses.dataclass(**DATACLASS_DEFAULTS)
class Marker(Base, BaseMarker):
    ...
