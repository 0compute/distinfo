from __future__ import annotations

from typing import TYPE_CHECKING

from distinfo import const
from distinfo.distribution import Distribution

from ..cases import Case

if TYPE_CHECKING:
    import pytest


class TestDistribution(Case):
    async def test_str(self) -> None:
        dist = await Distribution.factory()
        assert str(dist) == const.NULL_VALUE
        dist = await Distribution.factory(name="xxx")
        assert str(dist) == "xxx"
        dist = await Distribution.factory(name="xxx", version="1")
        assert str(dist) == "xxx-1"

    async def test_eq(self) -> None:
        dist = await Distribution.factory(name="xxx", version="1")
        dist2 = await Distribution.factory(name="xxx", version="1")
        assert dist == dist2
        dist2.version = "2"
        assert dist != dist2

    async def test_add_requirements(self, dist: Distribution) -> None:
        await dist.add_requirements("run", "xxx", "x")
        assert dist.requires.run == {"xxx"}
        await dist.add_requirements("test", "yyy; python_version > '1'")
        await dist.requires.evaluate()
        assert dist.requires.test == {"yyy"}
        await dist.add_requirements("xxx", "a", "a>=1", "a<2")
        assert dist.requires.xxx == {"a<2,>=1"}
        await dist.add_requirements("aaa", "£$%")
        assert "aaa" not in dist.requires

    async def test_add_requirement_extra(self, dist: Distribution) -> None:
        await dist.add_requirements("", "aaa[bbb]")
        assert (await dist.requires.evaluate()).run == {"aaa[bbb]"}

    async def test_factory_metadata(self) -> None:
        # metadata as arg
        dist = await Distribution.factory(dict(name="a"))
        assert dist.name == "a"

    async def test_exclude(self) -> None:
        dist = await Distribution.factory(_exclude=("bbb",))
        assert dist._excluded("bbb")
        assert not dist._excluded("readme")

    async def test_update(self, caplog: pytest.LogCaptureFixture) -> None:
        dist = await Distribution.factory(
            dict(license="aa", metadata_version="1"),
            version="1",
            _exclude=("summary",),
        )
        await dist.update(
            dict(
                name="Z",
                version="2",
                dynamic=["dependencies"],
                keywords=["a", "b", "c"],
                license="a",
                metadata_version="2",
                platform=[""],
                project_url="home, http://example.org",
                provides_extra=["dev", "test", "xxx"],
                requires_dist=[
                    "xxx; python_version > '1'",
                    "xxx1; python_version < '1'",
                    "yyy; extra == 'dev'",
                    "zzz; extra == 'test' and python_version > '1'",
                    "zzz1; extra == 'test' and python_version < '1'",
                    "aaa; python_version > '1' and extra == 'dev'",
                ],
                requires_python="",
                summary="XXX",
                ext=dict(x=1),
                unsupported=1,
            )
        )
        assert "unsupported key 'unsupported'" in caplog.text
        requires = await dist.requires.evaluate()
        assert list(requires.keys()) == ["dev", const.RUN_EXTRA, "test"]
        assert requires.run == {"xxx"}
        assert requires.dev == {"aaa", "yyy"}
        assert requires.test == {"zzz"}
        assert dist.platform == set()
        assert dist.requires_python is None
        assert dist.summary is None
        assert dist.metadata_version == "2"
        assert dist.license == "a"
        assert dist.name == "z"
        assert dist.version == "1"
        assert dist.keywords == {"a", "b", "c"}
        assert dist.ext.x == 1
        assert dist.project_url == {"Home, http://example.org"}
        await dist.update(license="aaa", metadata_version="1")
        assert dist.license == "a"
        assert dist.metadata_version == "2"

    async def test_update_alt_values(self) -> None:
        dist = await Distribution.factory(name="x")
        await dist.update(
            dict(
                home_page=const.NULL_VALUE,
                requires="yyy",  # pep 314 style
                requires_dist="zzz",
                keywords="a,b,c",
            )
        )
        assert (await dist.requires.evaluate()).run == {"yyy", "zzz"}
        assert dist.home_page is None
        assert dist.keywords == {"a", "b", "c"}
        await dist.update(
            dict(
                keywords="a b c",
            )
        )
        assert dist.keywords == {"a", "b", "c"}

    async def test_eval_requires(self, dist: Distribution) -> None:
        assert not await dist.requires.evaluate()
        requires_dist = {"a", "a>=1", "a<2", "b; python_version < '1'"}
        await dist.update(requires_dist=requires_dist)
        requires = await dist.requires.evaluate()
        # assert requires
        assert requires.run == {"a<2,>=1"}
        assert "Requires" in repr(requires)

    async def test_to_dict(self, dist: Distribution) -> None:
        odict = dist.to_dict()
        assert "requires" not in odict
        odict = dist.to_dict(core_metadata=True)
        assert "requires_dist" not in odict
        await dist.add_requirements("run", "xxx")
        await dist.add_requirements("dev", "yyy", "zzz; python_version > '1'")
        dist.ext.x = 1
        odict = dist.to_dict(core_metadata=True)
        assert odict.requires_dist == {
            "xxx",
            "yyy; extra == 'dev'",
            "zzz; extra == 'dev' and python_version > '1'",
        }
        await dist.requires.evaluate()
        odict = dist.to_dict()
        assert odict.name == "x"
        assert odict.requires.run == {"xxx"}
        assert odict.requires.dev == {"yyy", "zzz"}
        assert odict.ext.x == 1
        odict = dist.to_dict(core_metadata=True)
        assert odict.name == "x"
        assert odict.provides_extra == {"dev"}
        assert odict.requires_dist == {
            "xxx",
            "yyy; extra == 'dev'",
            "zzz; extra == 'dev' and python_version > '1'",
        }
        assert "ext" not in odict
        dist = await Distribution.factory(_exclude=("name",))
        odict = dist.to_dict()
        assert "name" not in odict
