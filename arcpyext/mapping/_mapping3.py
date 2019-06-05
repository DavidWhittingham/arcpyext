# coding=utf-8
"""This module contains extended functionality for related to the arcpy.mp module."""

# Python 2/3 compatibility
# pylint: disable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position
from __future__ import (absolute_import, division, print_function, unicode_literals)
from future.builtins.disabled import *
from future.builtins import *
from future.moves.itertools import zip_longest
from future.standard_library import install_aliases
install_aliases()
# pylint: enable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position

# Standard lib imports
import logging
import re
import zipfile

# Third-party imports
import arcpy

# Local imports
from ._cim import ProProject
from .. import _native as _prosdk
from ..exceptions import DataSourceUpdateError

# Configure module logging
logger = logging.getLogger("arcpyext.mapping")


def open_document(project):
    """Open an ArcGIS Pro Project from a given path.
    
    If the path is already a Project, this is a no-op.
    """

    if isinstance(project, arcpy.mp.ArcGISProject):
        return project

    return arcpy.mp.ArcGISProject(project)

def _native_document_open(proj_path):
    proj = ProProject(proj_path)
    proj.open()
    return proj

def _change_data_source(layer, new_props):
    try:
        existing_conn_props = layer.connectionProperties

        layer.updateConnectionProperties(existing_conn_props, new_props)

    except Exception as e:
        raise DataSourceUpdateError("Exception raised internally by ArcPy", layer, e)

    if hasattr(layer, "isBroken") and layer.isBroken:
        raise DataSourceUpdateError("Layer is now broken.", layer)


def _get_data_source_desc(layer_or_table):
    return layer_or_table.connectionProperties

def _native_list_maps(native_proj, arcpy_proj):
    return native_proj.maps

def _list_maps(proj):
    return proj.listMaps()

def _list_layers(proj, mp):
    return mp.listLayers()

def _list_tables(proj, mp):
    return mp.listTables()

def _describe_fields(layer_or_table_fields):
    raise NotImplementedError

def _describe_layer(layer):
    raise NotImplementedError

def _describe_table(table):
    raise NotImplementedError

def _get_spatial_ref(project, map):
    return arcpy.Describe(map).spatial_reference

def _native_describe_map(project, map):
    return {
        "name": map.name,
        "spatialReference": _get_spatial_ref(project, map),
        "layers": [_describe_layer(l) for l in _list_layers(project, map)],
        "tables": [_describe_table(t) for t in _list_tables(project, map)]
    }

def _describe_fields(native_layer_or_table_fields, layer_or_table_fields):

    if not layer_or_table_fields:
        return None

    return [
        {
            "alias": layer_or_table_fields[i].aliasName,
            "index": i,
            "name": layer_or_table_fields[i].baseName,
            "type": layer_or_table_fields[i].type,
            "visible": native_layer_or_table_fields[i].visible
        } for i in range(0, len(layer_or_table_fields))
    ]

def _native_describe_layer(native_layer, arcpy_map):
    arcpy_layer = arcpy_map.listLayers(native_layer.name)[0]

    layer_details = {
        "dataSource": arcpy_layer.dataSource,
        "database": None,
        "datasetName": arcpy_layer.connectionProperties["dataset"],
        "datasetType": arcpy_layer.connectionProperties["workspace_factory"],
        "definitionQuery": arcpy_layer.definitionQuery,
        "fields": _describe_fields(native_layer.feature_table.fields, arcpy.ListFields(arcpy_layer)),
        "index": None, # TODO
        "isBroken": arcpy_layer.isBroken,
        "isFeatureLayer": arcpy_layer.isFeatureLayer,
        "isNetworkAnalystLayer": arcpy_layer.isNetworkAnalystLayer,
        "isRasterLayer": arcpy_layer.isRasterLayer,
        "isRasterizingLayer": None, # Not implemented
        "isServiceLayer": None, # Not implemented
        "isGroupLayer": arcpy_layer.isGroupLayer,
        "longName": native_layer.long_name,
        "name": native_layer.name,
        "server": None,
        "serviceId": native_layer._cim_obj.ServiceLayerID,
        "userName": None,
        "visible": native_layer.visible

    }

    _add_data_connection_details(arcpy_layer, layer_details)

    return layer_details

def _native_describe_table(native_table, arcpy_map):
    arcpy_table = arcpy_map.listTables(native_table.name)[0]

    table_details = {
        "dataSource": arcpy_table.dataSource,
        "database": None,
        "datasetName": arcpy_table.connectionProperties["dataset"],
        "datasetType": arcpy_table.connectionProperties["workspace_factory"]
    }

    _add_data_connection_details(arcpy_table, table_details)

    return table_details

def _add_data_connection_details(arcpy_layer, layer_details):
    for key, value in arcpy_layer.connectionProperties["connection_info"].items():
        layer_details[key] = value

def _native_describe_map(native_pro_proj, arcpy_pro_proj, map_frame):
    arcpy_map = arcpy_pro_proj.listMaps(map_frame.name)[0]

    return {
        "name": map_frame.name,
        "spatialReference": map_frame.spatial_reference,
        "layers": [_native_describe_layer(l, arcpy_map) for l in _native_list_layers(native_pro_proj, map_frame)],
        "tables": [_native_describe_table(t, arcpy_map) for t in _native_list_tables(native_pro_proj, map_frame)]
    }

def _native_get_dataset_name(native_layer):
    pass

def _native_list_layers(pro_proj, map_frame):
    if map_frame.layers:
        return map_frame.layers
    else:
        return []


def _native_list_tables(pro_proj, map_frame):
    try:
        return map_frame.tables
    except AttributeError:
        return []

def _native_document_close(pro_proj):
    pro_proj.close()