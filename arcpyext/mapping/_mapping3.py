# coding=utf-8
"""This module contains extended functionality for related to the arcpy.mp module."""

# Python 2/3 compatibility
# pylint: disable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position
from __future__ import (absolute_import, division, print_function, unicode_literals)
from future.builtins.disabled import *
from future.builtins import *
from future.standard_library import install_aliases
install_aliases()
# pylint: enable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position

# Standard lib imports
import collections
import logging
import re
import zipfile

# Third-party imports
import arcpy

# Local imports
from ._cim import ProProject
from ._mapping_helpers import tokenise_table_name
from .. import _native as _prosdk
from .._patches._mp._cim_helpers import is_query_layer
from .._str import eformat, format_def_query
from ..exceptions import DataSourceUpdateError

# Put the map document class here so we can access the per-version type in a consistent location across Python versions
Document = arcpy.mp.ArcGISProject


def open_document(project):
    """Open an ArcGIS Pro Project from a given path.

    If the path is already a Project, this is a no-op.
    """

    if isinstance(project, arcpy.mp.ArcGISProject):
        return project

    return arcpy.mp.ArcGISProject(project)


def _change_data_source(layer, new_props):
    try:
        # updating of connection properties should always be assumed to be partial updates
        # must build dictionaries of partial attributes in order to update
        # the dictionary has to also deal with multiple levels of source/destination, to deal with relationships
        def get_paired_conn_props(original, new):
            matched_conn_props = {}
            new_conn_props = {}
            skip_this_level = False

            if "source" in original:
                # Connection properties has the 'source' part of a relationship, going down to next level
                source_matched, source_updated_conn_props = get_paired_conn_props(original["source"], new)
                matched_conn_props["source"] = source_matched
                new_conn_props["source"] = source_updated_conn_props
                skip_this_level = True

            if "destination" in original:
                # Connection properties has the 'destination' part of a relationship, going down to next level
                destination_matched, destination_updated_conn_props = get_paired_conn_props(
                    original["destination"], new)
                matched_conn_props["destination"] = destination_matched
                new_conn_props["destination"] = destination_updated_conn_props
                skip_this_level = True

            if skip_this_level:
                return (matched_conn_props, new_conn_props)

            for k in new:
                if k in original:
                    if isinstance(original[k], collections.Mapping) and isinstance(new[k], collections.Mapping):
                        matched_conn_props[k], new_conn_props[k] = get_paired_conn_props(original[k], new[k])
                    elif k in ["dataset", "featureDataset"]:
                        # process magic field updating
                        new_value = new[k]

                        # determine if dataset value needs formatting
                        needs_format = eformat.needs_formatting(new[k])

                        if needs_format:
                            if original[k] is not None:
                                # pass original value for parts
                                dataset_parts = tokenise_table_name(original[k])

                                # format new value, if necessary
                                new_value = eformat.format(new[k], **dataset_parts)
                                matched_conn_props[k] = original[k]
                                new_conn_props[k] = new_value
                        else:
                            matched_conn_props[k] = original[k]
                            new_conn_props[k] = new_value
                    else:
                        matched_conn_props[k] = original[k]
                        new_conn_props[k] = new[k]
                else:
                    new_conn_props[k] = new[k]

            return (matched_conn_props, new_conn_props)

        # pull out any options from new_props
        transform_options = {}
        if "transformOptions" in new_props:
            transform_options = new_props.pop("transformOptions")

        matched_conn_props, new_conn_props = get_paired_conn_props(layer.connectionProperties, new_props)

        logger = _get_logger()
        logger.debug("Matched conn props: %s", matched_conn_props)
        logger.debug("New conn props    : %s", new_conn_props)

        layer.updateConnectionProperties(matched_conn_props, new_conn_props, validate=False)

        if hasattr(layer, "isBroken") and layer.isBroken:
            raise DataSourceUpdateError("Layer is now broken.", layer)

        # process any transform options
        if "definitionQuery" in transform_options:
            # must format/replace definiton query
            def_query_opts = transform_options["definitionQuery"]
            layer.definitionQuery = format_def_query(layer.definitionQuery,
                                                     identifier_case=def_query_opts.get("identifierCase"),
                                                     identifier_quotes=def_query_opts.get("identifierQuotes"))

        # get the layer's CIM to process changes
        layer_cim = layer.getDefinition("V2")

        # get the table part of the CIM, unless the layer is a table already
        table_cim = layer_cim.featureTable if hasattr(layer_cim, "featureTable") else layer_cim

        # check if layer is a query layer, if so, don't continue, the definition can't be set safely
        if not is_query_layer(table_cim):
            if "fields" in transform_options:
                field_options = transform_options["fields"]

                # function for processing field name
                def get_field_name(field_name):
                    if "fieldNameMap" in field_options:
                        if field_name in field_options["fieldNameMap"]:
                            return field_options["fieldNameMap"][field_name]

                    if "fieldNameCase" in field_options:
                        field_name_template = "{}"
                        if field_options["fieldNameCase"].lower() == "lower":
                            field_name_template = "{:l}"
                        if field_options["fieldNameCase"].lower() == "upper":
                            field_name_template = "{:u}"

                        return eformat.format(field_name_template, field_name)

                    return field_name

                # handle field descriptions
                if hasattr(table_cim, "fieldDescriptions"):
                    for f in table_cim.fieldDescriptions:
                        f.fieldName = get_field_name(f.fieldName)

                # handle display fields (doesn't handle display field expressions)
                if hasattr(table_cim, "displayField"):
                    table_cim.displayField = get_field_name(table_cim.displayField)

            layer.setDefinition(layer_cim)

    except Exception as e:
        raise DataSourceUpdateError("Exception raised internally by ArcPy", layer, e)

    if hasattr(layer, "isBroken") and layer.isBroken:
        raise DataSourceUpdateError("Layer is now broken.", layer)


def _describe_map(file_path):
    ao_map_document = _native_document_open(file_path)

    try:
        # build return object
        return {
            "filePath": file_path,
            "maps":
            [_native_describe_map(ao_map_document, map_frame) for map_frame in _native_list_maps(ao_map_document)]
        }
    finally:
        _native_document_close(ao_map_document)


def _get_data_source_desc(layer_or_table):
    return layer_or_table.connectionProperties


def _get_logger():
    return logging.getLogger("arcpyext.mapping")


def _list_maps(proj):
    return proj.listMaps()


def _list_layers(proj, mp):
    return mp.listLayers()


def _list_tables(proj, mp):
    return mp.listTables()


def _native_add_data_connection_details(layer_table_parts, layer_table_details):
    l = layer_table_parts["arcpy"]
    if hasattr(l, "supports"):
        conn_props = l.connectionProperties if l.supports("CONNECTIONPROPERTIES") else None
    else:
        # this is a table, with no support for the "supports" function, but it should have connection properties
        conn_props = l.connectionProperties

    if not conn_props:
        return

    if "source" in conn_props:
        #this is a complex layer, e.g. has a join
        conn_props = conn_props.get("source")

    layer_table_details["datasetName"] = conn_props.get("dataset")
    layer_table_details["datasetType"] = conn_props.get("workspace_factory")

    conn_info = conn_props.get("connection_info", {})
    layer_table_details["database"] = conn_info.get("database")
    layer_table_details["server"] = conn_info.get("server")
    layer_table_details["service"] = conn_info.get("instance")
    layer_table_details["userName"] = conn_info.get("user")


def _native_document_close(proj_parts):
    proj_parts["prosdk"].close()
    proj_parts["prosdk"] = None
    proj_parts["arcpy"] = None


def _native_document_open(proj_path):
    proj = ProProject(proj_path)
    proj.open()

    return {"arcpy": arcpy.mp.ArcGISProject(proj_path), "prosdk": proj}


def _native_describe_fields(layer_or_table_fields):
    if not layer_or_table_fields:
        return None

    return [
        {
            "alias": f.alias,
            "index": i,
            "name": f.name,
            "type": None,  # Can't get this information yet
            "visible": f.visible
        } for i, f in enumerate(layer_or_table_fields)
    ]


def _native_describe_layer(layer_parts):
    # yapf: disable
    layer_details = {
        "dataSource": layer_parts["arcpy"].dataSource if layer_parts["arcpy"].supports("DATASOURCE") else None,
        "definitionQuery": layer_parts["arcpy"].definitionQuery if layer_parts["arcpy"].supports("DEFINITIONQUERY") else None,
        "fields":_native_describe_fields(layer_parts["prosdk"].feature_table.fields)
            if hasattr(layer_parts["prosdk"], "feature_table") else [],
        "index": layer_parts["index"],
        "isBroken": layer_parts["arcpy"].isBroken,
        "isFeatureLayer": layer_parts["arcpy"].isFeatureLayer,
        "isGroupLayer": layer_parts["arcpy"].isGroupLayer,
        "isNetworkAnalystLayer": layer_parts["arcpy"].isNetworkAnalystLayer,
        "isRasterLayer": layer_parts["arcpy"].isRasterLayer,
        "isRasterizingLayer": None,  # not implemented yet
        "isServiceLayer": layer_parts["arcpy"].isWebLayer,
        "longName": layer_parts["arcpy"].longName,
        "name": layer_parts["arcpy"].name,
        "serviceId": layer_parts["prosdk"].service_id,
        "visible": layer_parts["arcpy"].visible,

        # these get added with the call to _native_add_data_connection_details
        "database": None,
        "datasetName": None,
        "datasetType": None,
        "server": None,
        "service": None,
        "userName": None
    }
    # yapf: enable

    _native_add_data_connection_details(layer_parts, layer_details)

    return layer_details


def _native_describe_map(pro_proj, map_frame):

    return {
        "name": map_frame["arcpy"].name,
        "spatialReference": map_frame["prosdk"].spatial_reference.exportToString(),
        "layers": [_native_describe_layer(l) for l in _native_list_layers(pro_proj, map_frame)],
        "tables": [_native_describe_table(t) for t in _native_list_tables(pro_proj, map_frame)]
    }


def _native_describe_table(table_parts):
    table_details = {
        "dataSource": table_parts["arcpy"].dataSource,
        "definitionQuery": table_parts["arcpy"].definitionQuery,
        "fields": _native_describe_fields(table_parts["prosdk"].fields),
        "name": table_parts["arcpy"].name,
        "index": table_parts["index"],
        "isBroken": table_parts["arcpy"].isBroken,
        "serviceId": table_parts["prosdk"].service_id,

        # these get added with the call to _native_add_data_connection_details
        "database": None,
        "datasetName": None,
        "datasetType": None,
        "server": None,
        "service": None,
        "userName": None
    }

    _native_add_data_connection_details(table_parts, table_details)

    return table_details


def _native_list_layers(pro_proj, map_frame):
    arcpy_layers = map_frame["arcpy"].listLayers()
    prosdk_layers = map_frame["prosdk"].layers

    if not len(arcpy_layers) == len(prosdk_layers):
        raise ValueError("The number of layers from arcpy and from the ArcGIS Pro SDK are not the same.")

    layers = []

    for index, (arcpy_layer, prosdk_layer) in enumerate(zip(arcpy_layers, prosdk_layers)):
        if not arcpy_layer.name == prosdk_layer.name:
            raise ValueError(
                "Map from arcpy and map from ArcGIS Pro SDK do not have the same name, order likely not correct.")

        layers.append({"index": index, "arcpy": arcpy_layer, "prosdk": prosdk_layer})

    return layers


def _native_list_maps(pro_proj):
    arcpy_maps = pro_proj["arcpy"].listMaps()
    prosdk_maps = pro_proj["prosdk"].maps

    if not len(arcpy_maps) == len(prosdk_maps):
        raise ValueError("Length of native maps and length of ArcGIS Pro SDK maps is not the same.")

    maps = []

    for arcpy_map, prosdk_map in zip(arcpy_maps, prosdk_maps):
        if not arcpy_map.name == prosdk_map.name:
            raise ValueError(
                "Map from arcpy and map from ArcGIS Pro SDK do not have the same name, order likely not correct.")

        maps.append({"arcpy": arcpy_map, "prosdk": prosdk_map})

    return maps


def _native_list_tables(pro_proj, map_frame):
    arcpy_tables = map_frame["arcpy"].listTables()
    prosdk_tables = map_frame["prosdk"].tables

    if not len(arcpy_tables) == len(prosdk_tables):
        raise ValueError("The number of layers from arcpy and from the ArcGIS Pro SDK are not the same.")

    tables = []

    for index, (arcpy_table, prosdk_table) in enumerate(zip(arcpy_tables, prosdk_tables)):
        if not arcpy_table.name == prosdk_table.name:
            raise ValueError(
                "Map from arcpy and map from ArcGIS Pro SDK do not have the same name, order likely not correct.")

        tables.append({"index": index, "arcpy": arcpy_table, "prosdk": prosdk_table})

    return tables
