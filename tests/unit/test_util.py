from __future__ import annotations

import copy
import datetime
import io

import pytest
from box import Box

from distinfo import util

from ..cases import Case

ODICT = dict(
    one=list(),
    two=2,
    three=dict(x=1),
    four=False,
    five=None,
    six={2, 1},
    seven=datetime.datetime.now(),  # noqa: DTZ005
    eight=[9, 8],
    nine={},
    ten=[dict(a=1), {}],
)

ODICT_CLEAN = util.clean_dict(ODICT)

ODICT_DUMP_CLEAN = util.dump_dict(ODICT_CLEAN, stringify=True)


class TestUtil(Case):
    def test_irepr(self) -> None:
        assert util.irepr({"B", "a"}) == "'a', 'B'"

    def test_trepr(self) -> None:
        assert util.trepr("xxxx", max_length=4) == "'xxxx'"
        assert util.trepr("xxxxx", max_length=4) == "'xxx…'"
        assert util.trepr([1, 2, 3], max_length=4) == "[1, …]"
        assert util.trepr((1, 2, 3), max_length=4) == "(1, …)"
        assert util.trepr({1, 2, 3}, max_length=4) == "{1, …}"
        assert util.trepr(object(), max_length=4) == "<obj…>"
        assert util.trepr(dict(a=2, b=3, c=3), max_length=4) == "{'a'…}"

    def _assert_clean(self, odict: dict) -> None:
        assert "one" not in odict
        assert "two" in odict
        assert "three" in odict
        assert "four" in odict
        assert "five" not in odict
        assert "nine" not in odict
        assert odict["ten"] == [dict(a=1)]

    def test_clean_dict(self) -> None:
        odict = util.clean_dict(ODICT)
        self._assert_clean(odict)

    def test_clean_dict_inplace(self) -> None:
        odict = copy.deepcopy(ODICT)
        util.clean_dict(odict, inplace=True)
        self._assert_clean(odict)

    def test_clean_box(self) -> None:
        odict = Box(ODICT)
        util.clean_dict(odict, inplace=True)
        assert isinstance(odict, Box)
        self._assert_clean(odict)

    def test_dump_dict(self) -> None:
        odict = util.dump_dict(ODICT)
        assert odict["six"] == [1, 2]

    def test_list_to_set(self) -> None:
        odict = dict(a=[1, dict(b=1)], b=dict(c=[1]))
        clean = util.list_to_set(odict)
        assert clean == dict(a=[1, dict(b=1)], b=dict(c={1}))

    @pytest.mark.parametrize("fmt", util.DUMPERS)
    def test_dump_load(self, fmt: str) -> None:
        check = ODICT_DUMP_CLEAN
        # dump/load
        stream_cls = io.BytesIO if fmt == "msgpack" else io.StringIO
        stream = stream_cls()
        util.dump(ODICT, file=stream, fmt=fmt)
        stream.seek(0)
        dumped = util.load(file=stream, fmt=fmt)
        assert dumped == check
        # dumps/loads
        # FIXME: I've spent enough time fucking with mypy - the overload for dumps needs
        # fixing
        dump = util.dumps(ODICT, fmt=fmt)  # type: ignore[call-overload]
        dumped = util.loads(dump, fmt=fmt)
        assert dumped == check
        # box dumps/loads
        check = Box(a=1)
        dump = util.dumps(check, fmt=fmt)  # type: ignore[call-overload]
        dumped = util.loads(dump, fmt=fmt)
        assert dumped == check

    def test_log_duration(self, caplog: pytest.LogCaptureFixture) -> None:
        with util.log_duration("xxx"):
            pass
        assert "xxx in" in caplog.text

    async def test_tmpdir(self) -> None:
        async with util.tmpdir() as tmpdir:
            assert util.is_tmpdir(tmpdir)

    def test_cached_property(self) -> None:
        class TestCachedProperty:
            @util.cached_property
            def aproperty(self) -> int:
                return 1

        memoized = TestCachedProperty.aproperty.fget.memoize
        instance = TestCachedProperty()
        instance_key = memoized.get_key(memoized.keygen(instance))
        instance2 = TestCachedProperty()
        assert not memoized.memos
        assert instance.aproperty == 1
        assert instance_key in memoized.memos
        assert instance.aproperty == 1
        assert instance2.aproperty == 1
        assert len(memoized.memos) == 2
        del instance.aproperty
        assert instance_key not in memoized.memos
        assert len(memoized.memos) == 1
