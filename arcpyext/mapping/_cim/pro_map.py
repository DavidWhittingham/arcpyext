# coding=utf-8

# Python 2/3 compatibility
# pylint: disable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position,import-error,no-name-in-module
from __future__ import (absolute_import, division, print_function, unicode_literals)
from future.builtins.disabled import *
from future.builtins import *
from future.standard_library import install_aliases
install_aliases()
# pylint: enable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position,import-error,no-name-in-module

# Third-party imports
import arcpy

# Local imports
from .helpers import read_file_in_zip, passthrough_prop
from .factories import create_layer
from .tables import ProStandaloneTable

# .NET Imports
from ArcGIS.Core.CIM import CIMMap


class ProMap(object):

    _layers = None
    _spatial_reference = None
    _tables = None

    def __init__(self, proj_zip, map_string):
        self._proj_zip = proj_zip
        try:
            self._cim_obj = CIMMap.FromXml(map_string)
        except AttributeError:
            # probably in JSON format, try that
            self._cim_obj = CIMMap.FromJson(map_string)

    #region PROPERTIES

    description = passthrough_prop("Description")
    name = passthrough_prop("Name")

    @property
    def spatial_reference(self):
        if not self._spatial_reference:
            self._spatial_reference = arcpy.SpatialReference(self._cim_obj.SpatialReference.Wkid)

        return self._spatial_reference

    @property
    def layers(self):
        if self._layers is None:
            self._layers = []

            # guard against no layers in map
            if self._cim_obj.Layers:
                # layer paths are pre-pended with 'CIMPATH=', strip that to get the actual zip file path
                layer_paths = [lp[8:] for lp in self._cim_obj.Layers]

                # build layers recursively
                for lp in layer_paths:
                    self._create_layers(lp)

        # return a shallow copy so our internal list isn't altered
        return self._layers.copy()

    @property
    def tables(self):
        if self._tables is None:
            self._tables = []

            # table paths are pre-pended with 'CIMPATH=', strip that to get the actual zip file path
            table_paths = [tp[8:] for tp in (self._cim_obj.StandaloneTables or [])]

            # build tables
            for tp in table_paths:
                # get xml, determine type, create layer object, add to list
                table_string = read_file_in_zip(self._proj_zip, tp)

                self._tables.append(ProStandaloneTable(self._proj_zip, table_string))

        return self._tables.copy()

    #endregion

    def _create_layers(self, layer_path):
        # get xml, determine type, create layer object, add to list
        layer_string = read_file_in_zip(self._proj_zip, layer_path)

        layer_obj = create_layer(self._proj_zip, layer_string)
        self._layers.append(layer_obj)

        if layer_obj:
            for child_path in layer_obj._get_child_paths():
                child_layer = self._create_layers(child_path)

                # build parent/child relationships
                child_layer._parent = layer_obj
                layer_obj._children.append(child_layer)

        return layer_obj
