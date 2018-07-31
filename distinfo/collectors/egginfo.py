from email.parser import FeedParser
import logging

import pkg_resources

from .collector import Collector

log = logging.getLogger(__name__)


class EggInfo(Collector):

    MULTI_KEYS = (
        "classifier",
        "obsoletes",
        "obsoletes_dist",
        "platform",
        "project_url",
        "provides",
        "provides_dist",
        "provides_extra",
        "requires",
        "requires_dist",
        "requires_external",
        "supported_platform",
    )

    def _collect(self):

        pkg_infos = list(filter(
            lambda p: not str(p).startswith(".eggs/"),
            self.path.glob("**/PKG-INFO"),
        ))
        if not pkg_infos:
            log.warning("%r has no PKG-INFO", self)
            return
        pkg_info = pkg_infos[0]

        # parse metadata
        parser = FeedParser()
        parser.feed(pkg_info.open().read())
        message = parser.close()
        for key, value in message.items():
            value = value.strip()
            if not value or value == "UNKNOWN":
                continue
            key = key.lower().replace("-", "_")
            if key in self.MULTI_KEYS:
                self.metadata.setdefault(key, set()).add(value)
            else:
                self.metadata[key] = value

        # parse requires
        requires_path = pkg_info.parent / "requires.txt"
        if requires_path.exists():
            requires = requires_path.open().read()
            for extra, reqs in sorted(pkg_resources.split_sections(requires),
                                      key=lambda x: x[0] or ""):
                if extra is None:
                    extra = "run"
                for req in reqs:
                    self.add_requirement(req, extra)
