from __future__ import annotations

from typing import TYPE_CHECKING

import anyio
import atools
from box import Box
from packaging.markers import default_environment

from . import util
from .requirement import Requirement

if TYPE_CHECKING:
    from typing import Any

    from .requirement import BaseRequirement


class Requires(Box):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        object.__setattr__(self, "_dist", kwargs.pop("dist", None))
        object.__setattr__(self, "_evaled", False)  # noqa: FBT003
        object.__setattr__(self, "_raw", Box())
        super().__init__(*args, **kwargs)

    def __repr__(self) -> str:  # pragma: no ptest cover
        return f"{self.__class__.__name__}({self})"

    def __bool__(self) -> bool:
        return any(v for v in self.values())

    async def evaluate(self, *extras: str) -> Requires:
        env = self._env()
        async with anyio.create_task_group() as tg:
            for extra in extras if extras else self:  # type: ignore[attr-defined]
                for req in list(reqs := self.get(extra, set())):
                    tg.start_soon(
                        self._eval_req,
                        req,
                        reqs,
                        self._raw.setdefault(extra, set()),
                        env,
                    )
        util.clean_dict(self, inplace=True)
        util.clean_dict(self._raw, inplace=True)
        object.__setattr__(self, "_evaled", True)  # noqa: FBT003
        return self

    async def _eval_req(
        self,
        req: Requirement | str,
        reqs: set[Requirement | str],
        raw_reqs: set[Requirement],
        env: dict[str, str],
    ) -> None:
        reqs.remove(req)
        if isinstance(req, str):  # pragma: no ptest cover
            util.raise_on_hit()
            req = await self._requirement_factory(req)
        raw_reqs.add(req)
        if req.marker is not None and not req.marker.evaluate(env):
            return
        # set marker to None since it is no longer required
        reqs.add(req.replace(marker=None))

    async def _requirement_factory(self, reqstr: str) -> BaseRequirement:
        return Requirement.factory(reqstr)

    @staticmethod
    @atools.memoize
    def _env() -> (
        dict[str, str]
    ):  # pragma: no ptest cover - we override in test with static values for reproducibility
        return default_environment()
