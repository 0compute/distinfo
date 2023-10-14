from __future__ import annotations

from distinfo.base import Base


class Case(Base):
    def __str__(self) -> str:  # pragma: no cover
        # required for __repr__, needed for debugging tests
        return "test"
