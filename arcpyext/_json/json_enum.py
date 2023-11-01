# coding=utf-8
"""This module contains the JsonEnum base class."""

# Python 2/3 compatibility
# pylint: disable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position
from __future__ import (absolute_import, division, print_function, unicode_literals)
from future.builtins.disabled import *
from future.builtins import *
from future.standard_library import install_aliases
install_aliases()
from future.utils import iteritems
# pylint: enable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position

# Standard library imports
from aenum import Enum  # this is a backport package on Py2


class JsonEnum(Enum):
    def __iter__(self):
        return iteritems(self._to_jsonable())

    def _to_jsonable(self):
        return self.value