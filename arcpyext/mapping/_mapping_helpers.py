# coding=utf-8
"""This module contains shared internal functionality for mapping-related functions across arcpy versions."""

# Python 2/3 compatibility
# pylint: disable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position,import-error,no-name-in-module
from __future__ import (absolute_import, division, print_function, unicode_literals)
from future.builtins.disabled import *
from future.builtins import *
from future.standard_library import install_aliases
install_aliases()
from future.moves.collections import Mapping
from future.moves.itertools import chain, zip_longest
from future.utils import iteritems
# pylint: enable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position,import-error,no-name-in-module

import re


def tokenise_datasource(x):
    """Given a fully qualified feature class path, returns the feature class' schema, simple name and parent dataset (optional)"""

    regex = r"([\w\.]+)?(/|\\+)([\w\.]+$)"
    parts = re.search(regex, x, re.MULTILINE | re.IGNORECASE)

    if parts and len(parts.groups()) > 2:

        dataset = None if ".gdb" in parts.group(1).lower() or ".sde" in parts.group(1).lower() else tokenise_table_name(
            parts.group(1))
        table = tokenise_table_name(parts.group(3))

        return {
            "database": table["database"],
            "schema": None if table["schema"] is None else table["schema"],
            "dataSet": None if dataset is None else dataset["name"],
            "table": table["name"]
        }

    else:
        return None


def tokenise_table_name(table_name):
    """Given a feature class or feature dataset name, returns the schema (optional) and simple name"""

    dot_count = table_name.count(".")

    if dot_count == 2:
        dot_pos = [pos for pos, char in enumerate(table_name) if char == "."]

        return {
            "database": table_name[:dot_pos[0]],
            "schema": table_name[dot_pos[0] + 1:dot_pos[1]],
            "name": table_name[dot_pos[1] + 1:]
        }
    elif dot_count == 1:
        return {
            "database": None,
            "schema": table_name[:table_name.index(".")],
            "name": table_name[table_name.index(".") + 1:]
        }
    else:
        return {"database": None, "schema": None, "name": table_name}
