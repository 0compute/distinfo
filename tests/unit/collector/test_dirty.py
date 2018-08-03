from distinfo.collectors.dirty import Dirty

from .cases import Case


class TestDirty(Case):

    collector = Dirty

    def test_collect(self, tmpdir):
        tmpdir.join("xxx.pyc").write("")
        collector = self._collect(tmpdir)
        assert collector.ext.dirty

    def test_collect_empty(self, tmpdir):
        collector = super().test_collect_empty(tmpdir)
        assert "dirty" not in collector.ext
