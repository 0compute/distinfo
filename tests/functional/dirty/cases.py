from __future__ import annotations

from typing import TYPE_CHECKING, cast

from distinfo.collector import DirtyCollector

from ..cases import Case as BaseCase

if TYPE_CHECKING:
    from py.path import local

    from distinfo.collector.distcollector import DistCollectorOptionsType
    from distinfo.distribution import DistributionKeyType


class Case(BaseCase):
    async def _mk_collector(  # type: ignore[override]
        self,
        path: local,
        options: DistCollectorOptionsType = None,
        **kwargs: DistributionKeyType,
    ) -> DirtyCollector:
        if options is None:
            options = dict(modify_globals=True)
        return cast(
            DirtyCollector, await super()._mk_collector(path, options=options, **kwargs)
        )
