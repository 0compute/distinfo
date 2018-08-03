from ...base import Base

from .cases import Case


class Impl(Base):

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name


class TestDistribution(Case):

    def test_repr(self):
        impl = Impl("xxx")
        assert repr(impl) == "<Impl xxx>"

    def test_hash(self):
        impl = Impl("xxx")
        assert isinstance(hash(impl), int)

    def test_eq(self):
        impl = Impl("xxx")
        assert impl == "xxx"
        assert impl == Impl(name="xxx")
        assert impl != 1
