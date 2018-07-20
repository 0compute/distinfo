from __future__ import annotations

import pytest

from distinfo.requirement import Requirement as _Requirement

from ..cases import Case

# keep a reference to Requirement.__hash__ - the Base hash function is overridden by an
# autouse fixture "_patch_requirement_hash" - see ../conftest.py
base_hash = _Requirement.__hash__


class Requirement(_Requirement):
    __hash__ = base_hash


class TestRequirement(Case):
    def test_canonicalize_name(self) -> None:
        req = Requirement.factory("Test_me")
        assert req.name == "test-me"

    def test_str(self) -> None:
        reqstr = "a[x]>3; python_version > '1'"
        req = Requirement.factory(reqstr)
        assert str(req) == reqstr

    def test_eq(self) -> None:
        req = Requirement.factory("a")
        assert req == "a"
        assert req == Requirement.factory("a")
        assert req != 1

    def test_hash(self) -> None:
        req = Requirement.factory("xxx")
        assert hash(req) == hash("Requirementxxx")
        reqs = {req}
        assert req in reqs
        assert reqs == {req}
        reqs.remove(req)
        assert not reqs

    def test_order(self) -> None:
        req = Requirement.factory("a")
        req2 = Requirement.factory("b")
        assert req < req2

    def test_iand(self) -> None:
        # url
        req = Requirement.factory("aaa")
        req2 = Requirement.factory("aaa @ http://xxx/")
        req &= req2
        assert req == req2
        # specifier
        req = Requirement.factory("aaa")
        req2 = Requirement.factory("aaa>1")
        req &= req2
        assert req == req2
        # marker
        req = Requirement.factory("aaa")
        assert req.marker is None
        req &= req
        assert req.marker is None
        marker = 'python_version > "1"'
        req &= Requirement.factory(f"aaa; {marker}")
        req &= req
        assert str(req.marker) == marker
        marker2 = 'python_version < "2"'
        req &= Requirement.factory(f"aaa; {marker2}")
        assert str(req.marker) == f"{marker} and {marker2}"
        with pytest.raises(ValueError):
            req & Requirement.factory("bbb")

    def test_and(self) -> None:
        # url
        req = Requirement.factory("aaa")
        req2 = Requirement.factory("aaa @ http://xxx/")
        assert req & req2 == req2
        # specifier
        req2 = Requirement.factory("aaa>1")
        assert req & req2 == req2
        # marker
        req = Requirement.factory("aaa")
        assert req.marker is None
        assert (req & req).marker is None
        marker = 'python_version > "1"'
        req2 = Requirement.factory(f"aaa; {marker}")
        assert str((req & req2).marker) == marker
        marker2 = 'python_version < "2"'
        req3 = Requirement.factory(f"aaa; {marker2}")
        assert str((req2 & req3).marker) == f"{marker} and {marker2}"
        with pytest.raises(ValueError):
            req & Requirement.factory("bbb")

    def test_normalized_name(self) -> None:
        req = Requirement.factory("A")
        assert req.name == "a"
        assert req.name_base == "A"

    def test_parse(self) -> None:
        req = Requirement.factory("aaa[bbb]")
        assert req.name == "aaa"
        assert req.extras == {"bbb"}
        req = Requirement.factory("aaa <= 3")
        assert req.name == "aaa"
        assert req.specifier == "<=3"
        req = Requirement.factory("aaa (< 3); python_version > '1'")
        assert req == "aaa<3; python_version > '1'"
        req = Requirement.factory("aaa @ http://example/x")
        assert req == "aaa@ http://example/x"

    def test_specifier(self) -> None:
        req = Requirement.factory("xxx >= 1")
        req2 = Requirement.factory("xxx < 2")
        req.specifier &= req2.specifier
        assert req == "xxx<2,>=1"

    def test_in_set(self) -> None:
        req = Requirement.factory("xxx")
        req2 = Requirement.factory("yyy")
        reqs = {req, req2}
        assert reqs == {req2, req}
        assert reqs - {req2} == {req}

    def test_extras(self) -> None:
        req = Requirement.factory("x[one_two]")
        assert req.extras == {"one-two"}
        assert str(req) == "x[one-two]"

    def test_marker(self) -> None:
        req = Requirement.factory(
            "x; (os_name == 'posix' and python_version > '1') and extra == 'one_two'"
        )
        assert (
            str(req)
            == "x; extra == 'one-two' and os_name == 'posix' and python_version > '1'"
        )
        req2 = Requirement.factory(
            "x; os_name == 'posix' and python_version > '1' and extra == 'one-two'"
        )
        assert req == req2
