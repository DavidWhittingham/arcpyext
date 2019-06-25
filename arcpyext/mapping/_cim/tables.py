# coding=utf-8

# Python 2/3 compatibility
# pylint: disable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position,no-name-in-module,import-error
from __future__ import (absolute_import, division, print_function, unicode_literals)
from future.builtins.disabled import *
from future.builtins import *
from future.standard_library import install_aliases
install_aliases()
from future.utils import with_metaclass
# pylint: enable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position,no-name-in-module,import-error

# Standard lib imports
from abc import ABCMeta

# Local imports
from .helpers import passthrough_prop

# .NET Imports
from ArcGIS.Core.CIM import CIMStandaloneTable


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
            # there can be null field descriptions, test for that scenario
            if not self._cim_obj.FieldDescriptions:
                self._fields = []
            else:
                self._fields = [ProFieldDescription(cimfield) for cimfield in self._cim_obj.FieldDescriptions]

        return self._fields


class ProFeatureTable(ProDisplayTableBase):
    def __init__(self, cim_obj):
        super().__init__(cim_obj)


class ProStandaloneTable(ProDisplayTableBase):
    def __init__(self, proj_zip, xml_string):
        self._proj_zip = proj_zip
        super().__init__(CIMStandaloneTable.FromXml(xml_string))
    
    name = passthrough_prop("Name")
    service_id = passthrough_prop("ServiceTableID")