# coding=utf-8

# Python 2/3 compatibility
# pylint: disable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position
from __future__ import (absolute_import, division, print_function, unicode_literals)
from future.builtins.disabled import *
from future.builtins import *
from future.standard_library import install_aliases
install_aliases()
from future.moves.collections import deque
from future.moves.itertools import zip_longest
from future.utils import with_metaclass
# pylint: enable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position

# Standard lib imports
from abc import ABCMeta

# Local imports
from .helpers import passthrough_prop

class ProFieldDescription(object):

    _cim_obj = None

    def __init__(self, cim_obj):
        self._cim_obj = cim_obj

    alias = passthrough_prop("Alias")
    name = passthrough_prop("FieldName")
    visible = passthrough_prop("Visible")


class ProDisplayTableBase(with_metaclass(ABCMeta, object)):
    _fields = None

    def __init__(self, cim_obj):
        self._cim_obj = cim_obj

    definition_query = passthrough_prop("DefinitionExpression")

    @property
    def fields(self):
        if not self._fields:
            self._fields = [ProFieldDescription(cimfield) for cimfield in self._cim_obj.FieldDescriptions]

        return self._fields


class ProFeatureTable(ProDisplayTableBase):
    def __init__(self, cim_obj):
        super().__init__(cim_obj)
