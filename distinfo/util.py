from functools import partial
import json
import sys

from munch import unmunchify

import yaml

DUMPERS = dict(
    json=partial(json.dumps, default=str, sort_keys=True),
    yaml=partial(yaml.dump, default_flow_style=False),
    yamls=yaml.dump,
)

DEFAULT_DUMPER = "json"


def clean_dict(obj):
    drop = []
    for key, value in obj.items():
        if not isinstance(value, bool) and not value:
            drop.append(key)
        elif isinstance(value, dict):
            clean_dict(value)
            if not value:
                drop.append(key)
    for key in drop:
        del obj[key]


def _todict(obj):
    result = dict()
    for key, value in obj.items():
        if isinstance(value, dict):
            value = _todict(value)
        elif isinstance(value, set):
            value = sorted(map(str, value), key=str.lower)
        result[key] = value
    return unmunchify(result)


def dumps(obj, fmt=DEFAULT_DUMPER, **kwargs):
    return DUMPERS[fmt](_todict(obj), **kwargs).strip()


def dump(obj, file=sys.stdout, **kwargs):
    print(dumps(obj, **kwargs), file=file)


def dotget(obj, attrs, default=None):
    attrs = attrs.split(".")
    key = attrs.pop()
    for attr in attrs:
        obj = obj.get(attr, {})
    return obj.get(key, default)
