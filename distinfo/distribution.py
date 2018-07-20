from __future__ import annotations

import dataclasses
import functools
from typing import TYPE_CHECKING, ClassVar

import anyio
import deepmerge
from box import Box
from packaging.markers import Op, Value, Variable
from packaging.requirements import InvalidRequirement
from packaging.utils import canonicalize_name

from . import const, util
from .base import DATACLASS_DEFAULTS, Base
from .marker import Marker
from .requires import Requires

if TYPE_CHECKING:
    import email
    import logging

    from .requirement import Requirement

    BaseDistributionKeyType = set[str] | str | tuple
    DistributionDictKeyType = dict[str, BaseDistributionKeyType]
    # XXX: this isn't right - it doesn't deal with nested dicts properly
    DistributionRecDictKeyType = dict[
        str, BaseDistributionKeyType | DistributionDictKeyType
    ]
    DistributionKeyType = BaseDistributionKeyType | DistributionRecDictKeyType


@dataclasses.dataclass(kw_only=True, **DATACLASS_DEFAULTS)
class BaseDistribution:
    # core metadata fields, extended with all public fields of this class
    FIELDS: ClassVar[dict[str, Box | dataclasses.Field]] = dict(
        requires_dist=Box(default_factory=set),
    )

    # dummy for mypy because we use self.log, overridden by implementer
    log: ClassVar[logging.Logger]

    # core metadata keys minus requires_dist and provides_extra, which are implemented
    # as part of `to_dict`
    # https://packaging.python.org/en/latest/specifications/core-metadata/

    metadata_version: str | None = None

    name: str | None = None

    version: str | None = None

    dynamic: set[str] = dataclasses.field(default_factory=set)

    platform: set[str] = dataclasses.field(default_factory=set)

    supported_platform: set[str] = dataclasses.field(default_factory=set)

    summary: str | None = None

    description: str | None = None

    description_content_type: str | None = None

    # not specified as multi use, but is for our purposes
    keywords: set[str] = dataclasses.field(default_factory=set)

    home_page: str | None = None

    download_url: str | None = None

    # these 4 not in the spec as multi but effectively are as a consequence of PEP 621
    author: set[str] = dataclasses.field(default_factory=set)

    author_email: set[str] = dataclasses.field(default_factory=set)

    maintainer: set[str] = dataclasses.field(default_factory=set)

    maintainer_email: set[str] = dataclasses.field(default_factory=set)

    license: str | None = None  # noqa: A003

    classifier: set[str] = dataclasses.field(default_factory=set)

    requires_python: str | None = None

    requires_external: set[str] = dataclasses.field(default_factory=set)

    project_url: set[str] = dataclasses.field(default_factory=set)

    provides_dist: set[str] = dataclasses.field(default_factory=set)

    obsoletes_dist: set[str] = dataclasses.field(default_factory=set)

    # extra keys

    ext: Box = dataclasses.field(default_factory=Box)

    # class for Requires for ease of overriding
    REQUIRES_CLS: ClassVar[type] = Requires

    requires: Requires = dataclasses.field(init=False)

    # runtime state

    _init_keys: tuple

    _include: tuple = dataclasses.field(default_factory=tuple)

    _exclude: tuple = dataclasses.field(default_factory=tuple)

    def __post_init__(self) -> None:
        self.requires = self.REQUIRES_CLS(dist=self)

    @classmethod
    async def factory(
        cls,
        attrs: dict | email.Message | None = None,
        **kwargs: DistributionKeyType,
    ) -> BaseDistribution:
        requires = kwargs.pop("requires", None)
        self = cls(
            _init_keys=tuple(k for k in kwargs if not k.startswith("_")),
            **Box(util.list_to_set(kwargs)),
        )
        # convert requires str dict to Requires
        if requires is not None:  # pragma: no ptest cover
            for extra, reqstrs in requires.items():  # type: ignore[union-attr]
                self.requires[extra] = {
                    await self.requires._requirement_factory(reqstr)
                    for reqstr in reqstrs
                }
        if attrs is not None:  # pragma: no ftest ptest cover
            await self.update(attrs)
        return self

    def __str__(self) -> str:
        if self.name is None:
            return const.NULL_VALUE
        if self.version is None:
            return self.name
        return f"{self.name}-{self.version}"

    def to_dict(self, *, core_metadata: bool = False) -> Box:
        metadata = Box(
            {
                key: value
                for key, value in dataclasses.asdict(self).items()
                if value and not self._excluded(key)
            }
        )
        # core metadata compat: output requires as requires_dist and provides_extra
        if core_metadata:  # pragma: no ptest cover
            if requires := metadata.pop("requires", None):
                if self.requires._evaled:
                    requires = self.requires._raw
                metadata.requires_dist = set()
                metadata.provides_extra = set()
                for extra, reqs in requires.items():
                    for req in reqs:
                        if extra != const.RUN_EXTRA:
                            extra = extra.replace("_", "-")
                            metadata.provides_extra.add(extra)
                            marker = Marker.factory(
                                [(Variable("extra"), Op("=="), Value(extra))]
                            )
                            if req.marker:
                                marker &= req.marker
                            req = req.replace(marker=marker)
                        metadata.requires_dist.add(str(req))
            if "ext" in metadata:
                del metadata.ext
        return metadata

    async def update(
        self,
        attrs: dict[str, DistributionKeyType | list[str]] | email.Message = None,
        **kwargs: DistributionKeyType | list[str],
    ) -> None:
        multi = Box()

        for key, value in (attrs or kwargs).items():
            # normalize and look up key
            key = key.lower().replace("-", "_")
            if key in ("requires", "provides", "obsoletes") and isinstance(value, str):
                # old skool: https://peps.python.org/pep-0314/
                key += "_dist"
            if (field := self.FIELDS.get(key)) is None:
                # provides_extra is unused since we store extra as Requires keys
                if key != "provides_extra":  # pragma: no ptest cover
                    util.raise_on_hit()
                    self.log.warning(f"unsupported key {key!r}")
                continue

            # skip null values
            if isinstance(value, str):
                value = self._filter_value(value)
                if value is None:
                    continue

            # include/exclude keys
            if self._excluded(key):  # pragma: no ptest cover
                continue

            # fix up named keys
            if key == "name":
                value = canonicalize_name(value)
            elif key == "keywords":
                value = (
                    self._split_keywords(value)
                    if isinstance(value, str)
                    else functools.reduce(
                        lambda a, b: a | self._split_keywords(b), value, set()
                    )
                )

            # fix up multi-value keys
            if field.default_factory is set:
                if isinstance(value, str):
                    value = {value}
                else:
                    value = {v for v in {self._filter_value(v) for v in value} if v}
                if key == "project_url":
                    value = {v.capitalize() for v in value}
                if value:
                    multi.setdefault(key, set()).update(value)

            elif isinstance(value, dict):  # pragma: no ptest cover
                util.raise_on_hit()
                value = Box(util.list_to_set(value))
                deepmerge.always_merger.merge(getattr(self, key), value)

            # don't overwrite keys set in __init__
            elif key not in self._init_keys:  # pragma: no branch
                current = getattr(self, key)
                if current is not None:
                    # keep the highest metadata version
                    if key == "metadata_version":
                        value = max(current, value)
                        if current != value:  # pragma: no ptest cover
                            util.raise_on_hit()
                            current = None
                    # keep the shortest license because it may be a spdx id which is
                    # ideal
                    elif key == "license":
                        value = min(current, value)
                        if current != value:
                            current = None
                if value != current:
                    if current is not None:  # pragma: no ptest cover
                        util.raise_on_hit()
                        self.log.debug(
                            f"ignore overwrite: {key} {current!r} => {value!r}"
                        )
                    else:
                        setattr(self, key, value)

        # parse requires_dist to Requirement and set Requires
        if (requires_dist := multi.pop("requires_dist", None)) is not None:
            reqs: dict[str, Requirement] = {}
            async with anyio.create_task_group() as tg:
                for reqstr in requires_dist:
                    tg.start_soon(self._parse_reqstr, reqstr, reqs)
            for req in reqs.values():
                if req.marker is not None and req.marker.extras:
                    extras = req.marker.extras
                    req = req.replace(marker=req.marker.replace(extras=set()))
                else:
                    extras = {const.RUN_EXTRA}
                for extra in extras:
                    self.requires.setdefault(extra.replace("-", "_"), set()).add(req)

        # merge to self
        if multi:
            await self.merge(multi)

    async def merge(self, metadata: dict) -> None:
        for key, value in util.list_to_set(metadata).items():
            match current := getattr(self, key):
                case set():
                    current |= value
                case dict():
                    deepmerge.always_merger.merge(current, value)
                case _:
                    setattr(self, key, value)
            if key == "requires":
                for extra in value:
                    await self._merge_dupe_reqs(extra)

    async def add_requirements(self, extra: str, *reqstrs: str) -> None:
        if not extra:  # pragma: no ptest cover
            util.raise_on_hit()
            extra = const.RUN_EXTRA
        reqs: dict[str, Requirement] = {}
        async with anyio.create_task_group() as tg:
            for reqstr in reqstrs:
                tg.start_soon(self._parse_reqstr, reqstr, reqs)
        if filtered_reqs := set(reqs.values()):
            canonical_extra = canonicalize_name(extra).replace("-", "_")
            self.requires.setdefault(canonical_extra, set()).update(filtered_reqs)
            await self._merge_dupe_reqs(canonical_extra)

    async def _merge_dupe_reqs(self, extra: str) -> None:
        seen: dict[str, Requirement] = {}
        reqs = self.requires.get(extra, set())
        for req in list(reqs):
            if isinstance(req, str):
                reqs.remove(req)
                req = await self.requires._requirement_factory(req)
                reqs.add(req)
            if (base_req := seen.get(req.name + str(req.marker))) is None:
                seen[req.name + str(req.marker)] = req
            else:  # pragma: no ptest cover
                util.raise_on_hit()
                self.log.debug(f"merge dupe {req!r} of {base_req!r}")
                base_req &= req
                reqs.remove(req)

    @staticmethod
    def _filter_value(value: str) -> str | None:
        value = value.strip()
        if not (
            not value
            or value == const.NULL_VALUE
            or value == const.NULL_VERSION
            or value == "None"  # seen in `installer-0.5.1`
        ):
            return value

    @staticmethod
    def _split_keywords(value: str) -> set:
        # to spec is space-separated:
        #   https://peps.python.org/pep-0345/#keywords-optional
        # comma-separated is widely used:
        #   https://packaging.python.org/en/latest/specifications/core-metadata/#keywords
        return set(value.split(" " if " " in value else ","))

    async def _parse_reqstr(self, reqstr: str, reqs: dict) -> None:
        try:
            req = await self.requires._requirement_factory(reqstr)
        except InvalidRequirement as exc:
            self.log.debug(f"invalid requirement {reqstr!r}: {exc}")
        else:
            # ignore self-alias with no extras - seen in setupmeta
            if not (req.name == self.name and not req.extras):
                # merge same-named reqs
                existing_req = reqs.get(req.name + str(req.marker))
                if existing_req is not None:
                    existing_req &= req
                else:
                    reqs[req.name + str(req.marker)] = req

    def _excluded(self, key: str) -> bool:
        # "description" is "readme" in pyproject.toml
        if key == "readme":
            key = "description"
        elif key == "requires_dist":
            key = "requires"
        return (
            True
            if key.startswith("_")
            else (self._include and key not in self._include) or key in self._exclude
        )


BaseDistribution.FIELDS.update(
    {
        field.name: field
        for field in dataclasses.fields(BaseDistribution)
        if not field.name.startswith("_")
    }
)


@dataclasses.dataclass(**DATACLASS_DEFAULTS)
class Distribution(Base, BaseDistribution):
    ...
