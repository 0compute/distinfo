from __future__ import annotations

from typing import TYPE_CHECKING

from distinfo.base import Base

from ..cases import Case

if TYPE_CHECKING:
    import pytest


class BaseImpl(Base):
    def __init__(self, name: str):
        self.name = name

    def __str__(self) -> str:
        return self.name


class FailImpl(Base):
    def __str__(self) -> str:
        raise Exception


class TestBase(Case):
    def test_repr(self) -> None:
        impl = BaseImpl("xxx")
        assert repr(impl) == "<BaseImpl xxx>"
        impl2 = FailImpl()
        assert repr(impl2) == "<unprintable FailImpl>"

    def test_log_duration(self, caplog: pytest.LogCaptureFixture) -> None:
        impl = BaseImpl("xxx")
        with impl.log.duration("yyy"):
            pass
        assert "yyy in" in caplog.text
