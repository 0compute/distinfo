from __future__ import annotations

import os

import pytest

from distinfo import Requirement, logconfig, util
from distinfo.collector.metadata.dirty.dirtycollector import DirtyCollector


@pytest.fixture(autouse=True)
async def _logsetup() -> None:
    # this is in conjunction with "--show-capture=stderr" in pyproject.toml, we're not
    # using pytest's log capture because doing it this way gets us color
    await logconfig.configure(color="always", verbosity=3)


@pytest.fixture(autouse=True)
def _patch_requirement_hash(monkeypatch: pytest.MonkeyPatch) -> None:
    # this here for test sugar so we can assert that Requirements equal strings i.e.
    #   assert requires.test == {"something"}  noqa: ERA001
    monkeypatch.setattr(Requirement, "__hash__", lambda self: hash(str(self)))


@pytest.fixture(autouse=True)
def _setenv(monkeypatch: pytest.MonkeyPatch) -> None:
    os.environ[util.envvar("testing")] = "1"
    if "COVERAGE_PROCESS_START" in os.environ:  # pragma: no branch
        monkeypatch.setattr(
            DirtyCollector,
            "ENV_PASS",
            (*DirtyCollector.ENV_PASS, "COVERAGE_PROCESS_START"),
        )
