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

# Third-party imports
import arcpy

# Local imports
from .. import _native as _prosdk
from ..exceptions import DataSourceUpdateError
from ..arcobjects import init_arcobjects_context, destroy_arcobjects_context, list_layers

# Configure module logging
logger = logging.getLogger("arcpyext.mp")

def create_replacement_data_sources_list(document_data_sources_list,
                                         data_source_templates,
                                         raise_exception_no_change=False):

    # Here we are rearranging the data_source_templates so that the match criteria can be compared as a set - in case there are more than one.
    template_sets = [
        dict(list(template.items()) + [("matchCriteria", set(template["matchCriteria"].items()))])
        for template in data_source_templates
    ]

    # freeze values in dict for set comparison
    def freeze(d):
        """Freezes dicts and lists for set comparison."""
        if isinstance(d, dict):
            return frozenset((key, freeze(value)) for key, value in d.items())
        elif isinstance(d, list):
            return tuple(freeze(value) for value in d)
        return d

    def match_new_data_source(item):
        if item == None:
            return None

        new_conn = None
        for template in template_sets:
            # The item variable is a layer object which contains a fields property (type list) that can't be serialised and used in set operations
            # It is not required for datasource matching, so exclude it from the the set logic
            if template["matchCriteria"].issubset(set(freeze(item))):
                new_conn = template["dataSource"]
                break
        if new_conn == None and raise_exception_no_change:
            raise RuntimeError("No matching data source was found for layer")
        return new_conn

    return [{
        "layers": [match_new_data_source(layer) for layer in df["layers"]],
        "tableViews": [match_new_data_source(table) for table in df["tableViews"]]
    } for df in document_data_sources_list]


def open_document(project):
    """Open an ArcGIS Pro Project from a given path.
    
    If the path is already a Project, this is a no-op.
    """

    if isinstance(project, arcpy.mp.ArcGISProject):
        return project

    return arcpy.mp.ArcGISProject(project)


def validate_pro_project(project):
    # make sure the project is a project, not a path
    project = open_document(project)

    broken_layers = project.listBrokenDataSources()

    if len(broken_layers) > 0:
        logger.debug("Map '{0}': Broken data sources:".format(project.filePath))
        for layer in broken_layers:
            logger.debug(" {0}".format(layer.name))
            if not hasattr(layer, "supports"):
                #probably a TableView
                logger.debug("  workspace: {0}".format(layer.workspacePath))
                logger.debug("  datasource: {0}".format(layer.dataSource))
                continue

            #Some sort of layer
            if layer.supports("workspacePath"):
                logger.debug("  workspace: {0}".format(layer.workspacePath))
            if layer.supports("dataSource"):
                logger.debug("  datasource: {0}".format(layer.dataSource))

        return False

    return True


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


def _get_layer_details(layer):
    if layer.isGroupLayer and not layer.isNetworkAnalystLayer:
        return None

    details = {"name": layer.name, "longName": layer.longName}

    if layer.supports("datasetName"):
        details["datasetName"] = layer.datasetName

    if layer.supports("dataSource"):
        details["dataSource"] = layer.dataSource

    if layer.supports("serviceProperties"):
        details["serviceType"] = layer.serviceProperties["ServiceType"]

        if "UserName" in layer.serviceProperties:
            # File GDB doesn't support username and throws an exception
            details["userName"] = layer.serviceProperties["UserName"]

        if layer.serviceProperties["ServiceType"].upper() == "SDE":
            details["server"] = layer.serviceProperties["Server"]
            details["service"] = layer.serviceProperties["Service"]
            details["database"] = layer.serviceProperties["Database"]

    if layer.supports("workspacePath"):
        details["workspacePath"] = layer.workspacePath

    if layer.supports("visible"):
        details["visible"] = layer.visible

    if layer.supports("definitionQuery"):
        details["definitionQuery"] = layer.definitionQuery

    if layer.supports("connectionProperties"):
        details["connectionProperties"] = layer.connectionProperties

    # Fields
    # @see https://desktop.arcgis.com/en/arcmap/10.4/analyze/arcpy-functions/describe.htm
    # Wrapped in a try catch, because fields can only be resolved if the layer's datasource is valid.
    try:
        desc = arcpy.Describe(layer)
        logger.debug(desc)
        if desc.dataType == "FeatureLayer":
            field_info = desc.fieldInfo
            details["fields"] = []
            for index in range(0, field_info.count):
                details["fields"].append({
                    "index": index,
                    "name": field_info.getFieldName(index),
                    "visible": field_info.getVisible(index) == "VISIBLE"
                })
    except Exception:
        logger.exception("Could not resolve layer fields ({0}). The layer datasource may be broken".format(layer.name))

    return details


def _list_maps(proj):
    return proj.listMaps()


def _list_layers(proj, mp):
    return mp.listLayers()


def _list_tables(proj, mp):
    return mp.listTables()


def _get_table_details(table):
    return {
        "connectionProperties": table.connectionProperties,
        "dataSource": table.dataSource,
        "definitionQuery": table.definitionQuery,
        "name": table.name
    }
