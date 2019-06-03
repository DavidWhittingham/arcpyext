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


def _list_maps(proj):
    return proj.listMaps()


def _list_layers(proj, mp):
    return mp.listLayers()


def _list_tables(proj, mp):
    return mp.listTables()


def _native_document_open(proj_path):
    proj = ProProject(proj_path)
    proj.open()
    return proj


def _native_list_maps(pro_proj):
    return pro_proj.maps


def _native_describe_layer(layer):
    raise NotImplementedError()


def _native_describe_map(pro_proj, map_frame):
    return {
        "name": map_frame.name,
        "spatialReference": map_frame.spatial_reference,
        "layers": [_native_describe_layer(l) for l in _native_list_layers(pro_proj, map_frame)],
        "tables": [_native_describe_table(t) for t in _native_list_tables(pro_proj, map_frame)]
    }


def _native_describe_table(table):
    raise NotImplementedError()


def _native_list_layers(pro_proj, map_frame):
    return map_frame.layers


def _native_list_tables(pro_proj, map_frame):
    return map_frame.tables