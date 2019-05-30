# coding=utf-8
"""This module contains extended functionality for related to the arcpy.mapping module."""

# Python 2/3 compatibility
# pylint: disable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position
from __future__ import (absolute_import, division, print_function, unicode_literals)
from future.builtins.disabled import *
from future.builtins import *
from future.moves.collections import deque
from future.moves.itertools import zip_longest
from future.standard_library import install_aliases
from future.utils import viewitems
install_aliases()
# pylint: enable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position

# Standard lib imports
import ctypes
import logging
import os.path
import re

# Third-party imports
import arcpy
import olefile

# Local imports
from .. import _native as _ao
from ..exceptions import DataSourceUpdateError

# Configure module logging
logger = logging.getLogger("arcpyext.mapping")


def create_replacement_data_sources_list(document_data_sources_list,
                                         data_source_templates,
                                         raise_exception_no_change=False):
    template_sets = [
        dict(template.items() + [("matchCriteria", set(template["matchCriteria"].items()))])
        for template in data_source_templates
    ]

    logger.debug("Data source templates: %s", data_source_templates)

    # Given a feature class or feature dataset name, returns the schema (optional) and simple name
    def tokenise_table_name(x):
        if "." in x:
            return {"schema": x[:x.index(".")], "name": x[x.index(".") + 1:]}
        else:
            return {"schema": None, "name": x}

    # Given a fully qualified feature class path, returns the feature class' schema, simple name and parent dataset (optional)
    def tokenise_datasource(x):
        regex = r"([\w\.]+)?(/|\\+)([\w\.]+$)"
        parts = re.search(regex, x, re.MULTILINE | re.IGNORECASE)

        if parts and parts.groups > 3:

            dataset = None if ".gdb" in parts.group(1).lower() or ".sde" in parts.group(
                1).lower() else tokenise_table_name(parts.group(1))
            table = tokenise_table_name(parts.group(3))

            return {
                "schema": None if table["schema"] is None else table["schema"],
                "dataSet": None if dataset is None else dataset["name"],
                "table": table["name"]
            }

        else:
            return None

    def match_new_data_source(item):
        if item == None:
            return None

        logger.debug(item["datasetName"])
        logger.debug(item["workspacePath"])

        # Iterate through each template until we find a template that matches the item (i.e. layer or table)
        new_conn = None
        for template in template_sets:
            # The item variable is a layer object which contains a fields property (type list) that can't be serialised and used in set operations
            # It is not required for datasource matching, so exclude it from the the set logic
            hashable_layer_fields = [f for f in item.items() if not isinstance(f[1], list)]
            if template["matchCriteria"].issubset(set(hashable_layer_fields)):

                new_conn = template["dataSource"].copy()

                # Test #2: If the target workspace is a collection of workspaces, infer the target child workspace by using a
                # deterministic naming convention that maps the layer's dataset name to a workspace.
                if template.get("matchOptions", {}).get("isWorkspaceContainer") == True:

                    logger.debug("Data source template is workspace container.")

                    tokens = tokenise_datasource(item["dataSource"])

                    if tokens is not None:

                        logger.debug("Tokens are: %s", tokens)

                        if tokens["dataSet"] is not None and tokens["schema"] is not None:
                            logger.debug(1.11)
                            new_conn["workspacePath"] = "{}\\{}.{}.gdb".format(new_conn["workspacePath"],
                                                                               tokens["schema"], tokens["dataSet"])
                        elif tokens["dataSet"] is not None:
                            logger.debug(1.12)
                            new_conn["workspacePath"] = "{}\\{}.gdb".format(new_conn["workspacePath"],
                                                                            tokens["dataSet"])
                        else:
                            logger.debug(1.13)
                            new_conn["workspacePath"] = "{}\\{}.gdb".format(new_conn["workspacePath"], tokens["table"])

                break

        if new_conn == None and raise_exception_no_change:
            raise RuntimeError("No matching data source was found for layer")

        logger.debug("New connection: %s", new_conn)
        return new_conn

    return {
        "layers": [[match_new_data_source(layer) for layer in df] for df in document_data_sources_list["layers"]],
        "tableViews": [match_new_data_source(table) for table in document_data_sources_list["tableViews"]]
    }


def get_version(map_document):
    """Gets the version of a given map document (or path to a map document)."""

    if isinstance(map_document, arcpy.mapping.MapDocument):
        fp = map_document.filePath
    else:
        fp = map_document

    with olefile.OleFileIO(fp) as o, o.openstream("Version") as s:
        return s.read().decode("utf-16").split("\x00")[1]


def open_document(mxd):
    """Open a arcpy.mapping.MapDocument from a given path.
    
    If the path is already a MapDocument, this is a no-op.
    """

    import arcpy

    if isinstance(mxd, arcpy.mapping.MapDocument):
        return mxd

    return arcpy.mapping.MapDocument(mxd)


def _change_data_source(layer, new_layer_source):
    workspace_path = new_layer_source["workspacePath"]
    dataset_name = new_layer_source.get("datasetName")
    workspace_type = new_layer_source.get("workspaceType")
    schema = new_layer_source.get("schema")

    try:
        if ((not hasattr(layer, "supports") or layer.supports("workspacePath"))
                and (dataset_name == None and workspace_type == None and schema == None)):

            # Tests if layer is actually a layer object (i.e. has a "support" function) or table view (which doesn't,
            # but always supports "workspacePath").  Can't test on type (arcpy.mapping.TableView) as that doesn't work
            # on ArcPy 10.0

            layer.findAndReplaceWorkspacePath("", workspace_path, validate=False)
            return

        kwargs = {"validate": False}

        if dataset_name == None and hasattr(layer, "supports") and layer.supports("datasetName"):
            if layer.supports("workspacePath"):
                dataset_name = layer.dataSource.replace(layer.workspacePath, "")
            else:
                dataset_name = layer.datasetName

        if dataset_name != None:
            # break apart dataset_name into it's component parts
            ds_user, ds_name, fc_user, fc_name = _parse_data_source(dataset_name)

            if workspace_type == "FILEGDB_WORKSPACE":
                # file GDB's don't have schema/users, so if switching to that type, remove schema (if still included)
                dataset_name = fc_name
            elif schema != None:
                dataset_name = "{0}.{1}".format(schema, fc_name)

            kwargs["dataset_name"] = dataset_name

        if workspace_type != None:
            kwargs["workspace_type"] = workspace_type

        layer.replaceDataSource(workspace_path, **kwargs)

    except Exception as e:
        raise DataSourceUpdateError("Exception raised internally by ArcPy", layer, e)

    if hasattr(layer, "isBroken") and layer.isBroken:
        raise DataSourceUpdateError("Layer is now broken.", layer)


def _get_data_source_desc(layer_or_table):
    return layer_or_table.dataSource


def _get_spatial_ref(code):
    return arcpy.SpatialReference(code)


def _list_layers(map_document, data_frame):
    return arcpy.mapping.ListLayers(map_document, None, data_frame)


def _list_maps(map_document):
    return arcpy.mapping.ListDataFrames(map_document)


def _list_tables(map_document, data_frame):
    return arcpy.mapping.ListTableViews(map_document, None, data_frame)


def _native_add_data_connection_details(idataset, layer_details):
    if bool(idataset):
        # can enrich with database details
        connection_properties = dict(zip(*idataset.Workspace.ConnectionProperties.GetAllProperties()))
        layer_details["userName"] = connection_properties.get("USER")
        layer_details["server"] = connection_properties.get("SERVER")
        layer_details["service"] = connection_properties.get("INSTANCE")
        layer_details["database"] = connection_properties.get("DATABASE")

    # TODO: Implement details for web service layer


def _native_describe_fields(layer_or_table_fields):
    def field_type_id_to_name(f_type_id):
        field_types = [
            "SmallInteger", "Integer", "Single", "Double", "String", "Date", "OID", "Geometry", "Blob", "Raster",
            "Guid", "GlobalID", "Xml"
        ]

        if f_type_id >= 0 and f_type_id < len(field_types):
            return field_types[f_type_id]

        return None

    if not layer_or_table_fields:
        return None

    fields = [
        {
            "field": layer_or_table_fields.Field[i],
            "fieldInfo": layer_or_table_fields.FieldInfo[i],
            "index": i
        } for i in range(0, layer_or_table_fields.FieldCount)
    ]

    return [
        {
            "alias": f["fieldInfo"].Alias,
            "index": f["index"],
            "name": f["field"].Name,
            "type": field_type_id_to_name(f["field"].Type),
            "visible": f["fieldInfo"].Visible
        } for f in fields
    ]


def _native_describe_layer(layer_parts):
    layer_details = {
        "dataSource": _native_get_data_source(layer_parts),
        "database": None,
        "datasetName": _native_get_dataset_name(layer_parts["dataset"]),
        "datasetType": _native_get_dataset_type(layer_parts["dataset"]),
        "definitionQuery": _native_get_definition_query(layer_parts["featureLayerDefinition"]),
        "fields": _native_describe_fields(layer_parts["layerFields"]),
        "index": layer_parts["index"],
        "isBroken": not layer_parts["layer"].Valid,
        "isFeatureLayer": bool(layer_parts["featureLayer"]),
        "isNetworkAnalystLayer": bool(layer_parts["networkAnalystLayer"]),
        "isRasterLayer": bool(layer_parts["rasterLayer"]),
        "isRasterizingLayer": None,  # not implemented yet
        "isServiceLayer": None,  # not implemented yet
        "isGroupLayer": bool(layer_parts["groupLayer"]),
        "longName": "\\".join(_native_get_layer_name_parts(layer_parts)),
        "name": layer_parts["layer"].Name,
        "server": None,
        "service": None,
        "serviceId": _native_get_service_layer_property_value(layer_parts["serverLayerExtensions"], "ServiceLayerID"),
        "userName": None,
        "visible": layer_parts["layer"].Visible
    }

    _native_add_data_connection_details(layer_parts["dataset"], layer_details)

    return layer_details


def _native_describe_map(map_document, map_frame):
    return {
        "name": map_frame.Name,
        "spatialReference": _get_spatial_ref(_native_get_map_spatial_ref_code(map_document, map_frame)),
        "layers": [_native_describe_layer(l) for l in _native_list_layers(map_document, map_frame)],
        "tables": [_native_describe_table(t) for t in _native_list_tables(map_document, map_frame)]
    }


def _native_describe_table(table_parts):
    table_details = {
        "dataSource": _native_get_data_source(table_parts),
        "database": None,
        "datasetName": _native_get_dataset_name(table_parts["tableDataset"]),
        "datasetType": _native_get_dataset_type(table_parts["tableDataset"]),
        "definitionQuery": _native_get_definition_query(table_parts["standaloneTableDefinition"]),
        "fields": _native_describe_fields(table_parts["standaloneTableFields"]),
        "name": table_parts["standaloneTable"].Name,
        "index": table_parts["index"],
        "isBroken": not table_parts["standaloneTable"].Valid,
        "server": None,
        "service": None,
        "serviceId": _native_get_service_layer_property_value(table_parts["serverLayerExtensions"], "ServiceTableID"),
        "userName": None
    }

    _native_add_data_connection_details(table_parts["tableDataset"], table_details)

    return table_details


def _native_get_data_source(layer_or_table):
    """Attempts to get the path to the data source for a given layer or table."""
    path = None

    if layer_or_table.get("featureLayer"):
        # input is a feature layer
        if layer_or_table["featureLayer"].FeatureClass:
            feature_class_name = layer_or_table["dataset"].Name
            workspace_path = layer_or_table["dataset"].Workspace.PathName

            # Test if feature dataset in use, NULL COM pointers return falsey
            if layer_or_table["featureLayer"].FeatureClass.FeatureDataset:
                feature_dataset_name = layer_or_table["featureLayer"].FeatureClass.FeatureDataset.Name
                path = os.path.join(workspace_path, feature_dataset_name, feature_class_name)
            else:
                path = os.path.join(workspace_path, feature_class_name)
    elif layer_or_table.get("tableDataset"):
        # input is a standalone table
        table_name = layer_or_table["tableDataset"].Name
        workspace_path = layer_or_table["tableDataset"].Workspace.PathName
        path = os.path.join(workspace_path, table_name)

    return path


def _native_get_dataset_name(idataset):
    dataset_name = None

    if idataset:
        dataset_name = idataset.Name

    return dataset_name


def _native_get_dataset_type(idataset):
    dataset_type = None

    if idataset:
        dataset_type = idataset.Category

    return dataset_type


def _native_get_definition_query(feature_layer_or_table_definition):
    definition_query = None

    if feature_layer_or_table_definition:
        definition_query = feature_layer_or_table_definition.DefinitionExpression

    return definition_query


def _native_get_layer_name_parts(layer):

    name_parts = deque()

    def get_parent_layer_name(child_layer):
        # add to name parts
        name_parts.appendleft(child_layer["layer"].Name)

        if child_layer["parent"]:
            get_parent_layer_name(child_layer["parent"])

    get_parent_layer_name(layer)

    return name_parts


def _native_get_service_layer_property_value(service_layer_extensions, property_key):
    # flatten layer server extensions into a list of server property dictionaries
    # ServerProperties.GetAllProperties() returns two lists, names and values, so zip them and turn them into a
    # dictionary
    layer_extensions_server_properties = [
        p for p in (dict(zip(*sle.ServerProperties.GetAllProperties())) if bool(sle) else None
                    for sle in service_layer_extensions) if p is not None
    ]

    # find service layer ID, if it exists
    # value may be returned non-unique, this will be checked further up the stack
    service_layer_id = None
    for props in layer_extensions_server_properties:
        for key, value in viewitems(props):
            if key == property_key:
                return value

    return service_layer_id


def _native_list_layers(map_document, map_frame):
    """Recursively iterates through a map frame to get all layers, building up parent relationships as it goes."""

    # get the ArcObjects types we need
    import comtypes.gen.esriCarto as esriCarto
    import comtypes.gen.esriGeoDatabase as esriGeoDatabase
    import comtypes.gen.esriNetworkAnalyst as esriNetworkAnalyst
    import comtypes.gen.esriSystem as esriSystem

    # list of all layers that we'll be returning
    layers = []

    def build_layer_parts(map_layer):
        layer_parts = {
            "children": [],
            "dataset": None,
            "layer": _ao.cast_obj(map_layer, esriCarto.ILayer2),
            "layerFields": _ao.cast_obj(map_layer, esriCarto.ILayerFields),
            "featureLayer": _ao.cast_obj(map_layer, esriCarto.IFeatureLayer),
            "featureLayerDefinition": _ao.cast_obj(map_layer, esriCarto.IFeatureLayerDefinition2),
            "groupLayer": _ao.cast_obj(map_layer, esriCarto.IGroupLayer),
            "index": len(layers),  # map index will be the same as the current length of this array
            "networkAnalystLayer": _ao.cast_obj(map_layer, esriNetworkAnalyst.INALayer),
            "parent": None,
            "rasterLayer": _ao.cast_obj(map_layer, esriCarto.IRasterLayer),
            "serverLayerExtensions": None
        }

        if bool(layer_parts["featureLayer"]):
            layer_parts["dataset"] = _ao.cast_obj(layer_parts["featureLayer"].FeatureClass, esriGeoDatabase.IDataset)

        # Get server layer extensions
        layer_extensions = _ao.cast_obj(map_layer, esriCarto.ILayerExtensions)
        layer_parts["serverLayerExtensions"] = [
            _ao.cast_obj(layer_extensions.Extension(i), esriCarto.IServerLayerExtension)
            for i in range(0, layer_extensions.ExtensionCount)
        ]

        layers.append(layer_parts)

        return layer_parts

    def get_child_layers(layer_parts, parent_parts):
        # Set parent
        layer_parts["parent"] = parent_parts

        if not bool(layer_parts["groupLayer"]):
            # layer is not a group layer, ignore
            return

        # layer is a group layer, cast to ICompositeLayer to get access to child layers
        composite_layer = _ao.cast_obj(layer_parts["layer"], esriCarto.ICompositeLayer)
        for i in range(0, composite_layer.Count):
            # get child layer
            child_layer = composite_layer.Layer[i]

            # get child layer parts
            child_layer_parts = build_layer_parts(child_layer)

            # add child_layer_parts to the list of children for the current layer
            layer_parts["children"].append(child_layer_parts)

            # recursively find children
            get_child_layers(child_layer_parts, layer_parts)

    # iterate through the top level of layers
    map_layer_iterator = map_frame.Layers(None, False)
    map_layer = map_layer_iterator.Next()
    while (map_layer):
        layer_parts = build_layer_parts(map_layer)
        get_child_layers(layer_parts, None)

        map_layer = map_layer_iterator.Next()

    return layers


def _native_list_maps(map_document):
    """Gets a list of IMaps (Data Frames) from the provided map document."""

    # get the ArcObjects types we need
    import comtypes.gen.esriCarto as esriCarto

    # make sure map document is a map document
    map_document = _ao.cast_obj(map_document, esriCarto.IMapDocument)

    # iterate the list of maps, casting each one to IMap
    return [_ao.cast_obj(map_document.Map[i], esriCarto.IMap) for i in range(0, map_document.MapCount)]


def _native_list_tables(map_document, map_frame):
    """Iterates through a map frame to get all tables."""

    # get the ArcObjects types we need
    import comtypes.gen.esriCarto as esriCarto
    import comtypes.gen.esriGeoDatabase as esriGeoDatabase

    # list of all tables
    tables = []

    def build_table_parts(standalone_table):
        table_parts = {
            "index": len(tables),  # map index will be the same as the current length of this array
            "standaloneTable": standalone_table,
            "standaloneTableDataset": _ao.cast_obj(standalone_table, esriGeoDatabase.IDataset),
            "standaloneTableDefinition": _ao.cast_obj(standalone_table, esriCarto.ITableDefinition),
            "standaloneTableFields": _ao.cast_obj(standalone_table, esriGeoDatabase.ITableFields),
            "table": standalone_table.Table,
            "tableDataset": _ao.cast_obj(standalone_table.Table, esriGeoDatabase.IDataset),
            "serverLayerExtensions": None
        }

        # Get server layer extensions
        table_extensions = _ao.cast_obj(standalone_table, esriCarto.ITableExtensions)
        table_parts["serverLayerExtensions"] = [
            sle for sle in (_ao.cast_obj(table_extensions.Extension(i), esriCarto.IServerLayerExtension)
                            for i in range(0, table_extensions.ExtensionCount)) if sle is not None
        ]

        tables.append(table_parts)

        return table_parts

    # cast map to a standalone table collection to get access to tables
    table_collection = _ao.cast_obj(map_frame, esriCarto.IStandaloneTableCollection)

    # iterate the table collection
    for i in range(0, table_collection.StandaloneTableCount):
        table = table_collection.StandaloneTable[i]
        build_table_parts(table)

    return tables


def _native_get_map_spatial_ref_code(map_document, map_frame):
    return map_frame.spatialReference.FactoryCode


def _native_mxd_exists(mxd_path):
    import comtypes.gen.esriCarto as esriCarto

    map_document = _ao.create_obj(esriCarto.MapDocument, esriCarto.IMapDocument)
    exists = map_document.IsPresent(mxd_path)
    valid = map_document.IsMapDocument(mxd_path)
    return exists and valid


def _native_document_close(map_document):
    import comtypes.gen.esriCarto as esriCarto

    # Make sure it's a map document
    map_document = _ao.cast_obj(map_document, esriCarto.IMapDocument)
    map_document.Close()


def _native_document_open(mxd_path):
    import comtypes.gen.esriCarto as esriCarto

    if _native_mxd_exists(mxd_path):
        map_document = _ao.create_obj(esriCarto.MapDocument, esriCarto.IMapDocument)
        map_document.Open(mxd_path)

        # Maps must be activated in order to get all properties to be initialized
        maps = _native_list_maps(map_document)
        window_handle = ctypes.windll.user32.GetDesktopWindow()
        for m in maps:
            active_view = _ao.cast_obj(m, esriCarto.IActiveView)
            active_view.Activate(window_handle)

        return map_document
    else:
        raise ValueError("'mxd_path' not found or invalid.")


def _parse_data_source(data_source):
    """Takes a string describing a data source and returns a four-part tuple describing the dataset username, dataset
    name, feature class username and feature class name"""

    dataset_regex = re.compile(
        r"^(?:\\)?(?P<ds_user>[\w]*?)(?:\.)?(?P<ds_name>[\w]*?(?=\\))(?:\\)?(?P<fc_user>[\w]*?(?=\.))(?:\.)(?P<fc_name>[\w]*?)$",
        re.IGNORECASE)

    r = dataset_regex.search(data_source)

    if r == None:
        feature_class_regex = re.compile(r"^(?:\\)?(?P<fc_user>[\w]*?(?=\.))(?:\.)(?P<fc_name>[\w]*?)$", re.IGNORECASE)
        r = feature_class_regex.search(data_source)

    if r == None:
        return (None, None, None, data_source)

    r = r.groupdict()

    return (r.get("ds_user"), r.get("ds_name"), r.get("fc_user"), r.get("fc_name"))
