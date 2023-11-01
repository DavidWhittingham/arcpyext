# coding=utf-8
"""This module contains helper functions used in making map document/project comparisons."""

# Python 2/3 compatibility
# pylint: disable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position,import-error,no-name-in-module
from __future__ import (absolute_import, division, print_function, unicode_literals)
from future.builtins.disabled import *
from future.builtins import *
from future.standard_library import install_aliases
install_aliases()
from future.utils import iteritems
# pylint: enable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position,import-error,no-name-in-module

try:
    from collections.abc import Mapping, Sequence
except ImportError:
    from collections import Mapping, Sequence


def dictionaries_eq(a, b):
    return set(iteritems(a)) == set(iteritems(b))


def dictionaries_eq_ignore_case(a, b):
    a = lowercase_dict(a)
    b = lowercase_dict(b)

    return dictionaries_eq(a, b)


def lowercase_dict(d):
    def process_value(v):
        if isinstance(v, Mapping):
            return lowercase_dict(v)
        elif isinstance(v, ("".__class__, u"".__class__, b"".__class__)):
            return v.lower()
        elif isinstance(v, Sequence):
            return [process_value(sv) for sv in v]
        else:
            return v

    return {k: process_value(v) for (k, v) in iteritems(d)}


def get_datasource_info(layer_desc):
    # wrapped in str to ensure consistant type across source and Py versions
    return {
        "workspacePath": str(layer_desc.get("workspacePath", "")),
        "datasetName": str(layer_desc.get("datasetName", "")),
        "database": str(layer_desc.get("database", "")),
        "server": str(layer_desc.get("server", "")),
        "service": str(layer_desc.get("service", ""))
    }


def get_dict_subset(d, *keys):
    return {k: d[k] for k in keys}


def get_fields_compare_info(fields):
    return [get_dict_subset(f, "name", "type") for f in fields if f["visible"]]


def is_superset(superset, subset):
    return all(item in superset for item in subset)


def recursive_sort(obj):
    """
    Recursively sort lists/dictionaries for consistent comparison.
    """

    if isinstance(obj, dict):
        return sorted((k, recursive_sort(v)) for k, v in obj.items())
    if isinstance(obj, list):
        return sorted(recursive_sort(x) for x in obj)
    else:
        return obj
