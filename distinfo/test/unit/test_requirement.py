from ...requirement import Requirement

from .cases import Case

REQUIREMENTS = """
aaa
http://h/p
-cxxx
"""


class TestRequirement(Case):

    def test_from_file(self, tmpdir):
        requirements = "requirements.txt"
        reqs = tmpdir.join(requirements)
        reqs.write(REQUIREMENTS)
        assert list(Requirement.from_file(reqs)) == ["aaa", "http://h/p"]

    def test_is_named(self):
        req = Requirement(name=None)
        assert not req.is_named
