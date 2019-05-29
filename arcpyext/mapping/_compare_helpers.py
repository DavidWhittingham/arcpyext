# coding=utf-8
"""This module contains helper functions used in making map document/project comparisons."""

# Python 2/3 compatibility
# pylint: disable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position
from __future__ import (absolute_import, division, print_function, unicode_literals)
from future.builtins.disabled import *
from future.builtins import *
from future.standard_library import install_aliases
install_aliases()
from future.utils import iteritems
# pylint: enable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position


def get_datasource_info(layer_desc):
    # wrapped in str to ensure consistant type across source and Py versions
    return {
        "workspacePath": str(layer_desc.get("workspacePath", "")),
        "datasetName": str(layer_desc.get("datasetName", "")),
        "database": str(layer_desc.get("database", "")),
        "server": str(layer_desc.get("server", "")),
        "service": str(layer_desc.get("service", "")),
    }


def dictionaries_eq(a, b):
    return set(iteritems(a)) == set(iteritems(b))


def dictionaries_eq_ignore_case(a, b):
    lowercase_dict = lambda d: {k: v.lower() if isinstance(v, str) else v for (k, v) in iteritems(d)}

    a = lowercase_dict(a)
    b = lowercase_dict(b)

    return dictionaries_eq(a, b)

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