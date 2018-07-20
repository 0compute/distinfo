from __future__ import annotations

import pytest

from distinfo.distribution import Distribution


@pytest.fixture()
async def dist() -> Distribution:
    return await Distribution.factory(name="x")
