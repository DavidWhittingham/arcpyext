# coding=utf-8
"""This module contains a custom JSON encoder for writing out objects to JSON that have a custom JSON-crafting function."""

# Python 2/3 compatibility
# pylint: disable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position
from __future__ import (absolute_import, division, print_function, unicode_literals)
from future.builtins.disabled import *
from future.builtins import *
from future.standard_library import install_aliases
install_aliases()
# pylint: enable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position

from json import JSONEncoder


class ToJsonEncoder(JSONEncoder):
    def default(self, obj):
        if hasattr(obj, "_to_jsonable"):
            return obj._to_jsonable()
        return JSONEncoder.default(self, obj)