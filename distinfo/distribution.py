import importlib
import logging

from munch import DefaultMunch, Munch

from packaging.markers import Marker

import pkg_resources

from requirementslib.utils import pep423_name

from setuptools import sandbox

from . import const
from .base import Base
from .config import cfg
from .requirement import Requirement

log = logging.getLogger(__name__)


class Distribution(Base):

    IMPLICIT_PACKAGES = ("setuptools", "wheel")

    def __init__(self, req=None, **kwargs):
        self.req = req
        self.metadata = Munch(
            name="UNKNOWN",
            version="0.0.0",
            provides_extra=set(),
            requires_dist=set(),
            extensions=Munch(distinfo=Munch()),
        )
        self.metadata.update({k: set(v) if k in const.METADATA_MULTI else v
                              for k, v in kwargs.items()})
        if self.req is not None and self.req.is_file_or_url:
            with sandbox.pushd(self.req.req.path):
                for name in cfg.collectors:
                    module = importlib.import_module(
                        "distinfo.collectors.%s" % name.lower()
                    )
                    getattr(module, name)(self).collect()

    def __str__(self):
        return "%s-%s" % (self.name, self.version)

    @property
    def name(self):
        return self.metadata.name

    @name.setter
    def name(self, name):
        self.metadata.name = name

    @property
    def normalized_name(self):
        return pep423_name(self.name)

    @property
    def version(self):
        return self.metadata.version

    @property
    def provides_extra(self):
        return self.metadata.provides_extra

    @property
    def requires_dist(self):
        return self.metadata.requires_dist

    @property
    def ext(self):
        return self.metadata.extensions.distinfo

    def _filter_reqs(self, reqs, extra):
        filtered = set()
        env = dict(extra=extra)
        for req in reqs:
            if extra == "run":
                if req.markers is None or Marker(req.markers).evaluate(env):
                    filtered.add(req)
            else:
                if req.markers is not None and Marker(req.markers).evaluate(env):
                    filtered.add(req)
        return filtered

    @property
    def requires(self):
        reqs = set(map(Requirement.from_line, self.requires_dist))
        requires = DefaultMunch(set())
        run = self._filter_reqs(reqs, "run")
        if run:
            requires["run"] = run
            reqs -= run
        for extra in self.provides_extra:
            ereqs = self._filter_reqs(reqs, extra)
            if ereqs:
                # drop marker as no longer required
                requires[extra] = set(map(
                    lambda r: setattr(r, "markers", None) or r,
                    ereqs,
                ))
        return requires

    def add_requirement(self, req, extra="run"):

        # cast to Requirement
        if not isinstance(req, Requirement):
            try:
                req = Requirement.from_line(req)
            except (pkg_resources.RequirementParseError, ValueError) as exc:
                log.warning("%r %r add %r raised %r", self, extra, req, exc)
                return

        if not req.is_named:
            log.warning("%r ignoring unnamed %r", self, req)
            return

        # skip out for implicit requirements
        if req.name in self.IMPLICIT_PACKAGES:
            return

        # check existing requirement
        for ereq in self.requires[extra] \
                | (extra != "run" and self.requires["run"] or set()):
            if ereq.normalized_name == req.normalized_name:
                return

        if extra != "run":
            if ":" in extra:  # setuptools extra:condition syntax
                extra, condition = extra.split(":", 1)
                if not Marker(condition).evaluate():
                    return
            if extra:
                extra = pkg_resources.safe_extra(extra)
                self.provides_extra.add(extra)
                req.markers = req.req.markers = "extra == '%s'" % extra

        self.requires_dist.add(str(req))
        return req
