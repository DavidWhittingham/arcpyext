# coding=utf-8
"""This module contains extended functionality for related to the arcpy.mapping module."""

# Python 2/3 compatibility
# pylint: disable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position
from __future__ import (absolute_import, division, print_function, unicode_literals)
from future.builtins.disabled import *
from future.builtins import *
from future.standard_library import install_aliases
install_aliases()
from future.moves.collections import deque
from future.utils import viewitems
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

# .NET Imports
import System.Runtime.InteropServices

# Put the map document class here so we can access the per-version type in a consistent location across Python versions
Document = arcpy.mapping.MapDocument


def get_version(map_document):
    """Gets the version of a given map document (or path to a map document)."""

    if isinstance(map_document, arcpy.mapping.MapDocument):
        fp = map_document.filePath
    else:
        fp = map_document

    with olefile.OleFileIO(fp) as o:
        if o.exists("Version"):
            with o.openstream("Version") as s:
                return s.read().decode("utf-16").split("\x00")[1]

    return None


def open_document(mxd):
    """Open a arcpy.mapping.MapDocument from a given path.
    
    If the path is already a MapDocument, this is a no-op.
    """

    import arcpy

    if isinstance(mxd, arcpy.mapping.MapDocument):
        return mxd

    return arcpy.mapping.MapDocument(mxd)


def _change_data_source(layer, new_layer_source):
    logger = _get_logger()
    workspace_path = new_layer_source["workspacePath"]
    dataset_name = new_layer_source.get("datasetName")
    workspace_type = new_layer_source.get("workspaceType")
    schema = new_layer_source.get("schema")

    logger.debug("Workspace path: {}".format(workspace_path))
    logger.debug("Dataset name: {}".format(dataset_name))
    logger.debug("Workspace type: {}".format(workspace_type))
    logger.debug("Schema: {}".format(schema))

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
        logger.exception("Exception raised by ArcPy")
        raise DataSourceUpdateError("Exception raised internally by ArcPy", layer, e)

    if hasattr(layer, "isBroken") and layer.isBroken:
        raise DataSourceUpdateError("Layer is now broken.", layer)


def _describe_map(file_path):
    with _ao.ComReleaser() as com_releaser:
        # open the MXD in ArcObjects
        ao_map_document = _native_document_open(file_path)

        # add the ArcObjects document to the com_releaser
        com_releaser.manage_lifetime(ao_map_document)

        # base description layout
        desc = {"filePath": file_path, "maps": []}

        for map_frame in _native_list_maps(ao_map_document):
            # add the ArcObjects map frame to the com_releaser
            com_releaser.manage_lifetime(map_frame)

            # add the map description to the output object
            desc["maps"].append(_native_describe_map(ao_map_document, map_frame))

        _native_document_close(ao_map_document)

        return desc


def _get_data_source_desc(layer_or_table):
    if hasattr(layer_or_table, "supports"):
        if not layer_or_table.supports("DATASOURCE"):
            return None

    return layer_or_table.dataSource


def _get_logger():
    return logging.getLogger("arcpyext.mapping")


def _get_spatial_ref(code):
    return arcpy.SpatialReference(code)


def _list_layers(map_document, data_frame):
    return arcpy.mapping.ListLayers(map_document, None, data_frame)


def _list_maps(map_document):
    return arcpy.mapping.ListDataFrames(map_document)


def _list_tables(map_document, data_frame):
    return arcpy.mapping.ListTableViews(map_document, None, data_frame)


def _native_add_data_connection_details(idataset, layer_details):
    import ESRI.ArcGIS.Geodatabase as esriGeoDatabase
    import ESRI.ArcGIS.esriSystem as esriSystem

    if bool(idataset):
        # can enrich with database details
        workspace = _ao.cast_obj(idataset.Workspace, esriGeoDatabase.IWorkspace)
        property_set = _ao.cast_obj(workspace.ConnectionProperties, esriSystem.IPropertySet)
        _, property_keys, property_values = property_set.GetAllProperties(None, None)

        connection_properties = dict(zip(property_keys, property_values))
        layer_details["userName"] = connection_properties.get("USER")
        layer_details["server"] = connection_properties.get("SERVER")
        layer_details["service"] = connection_properties.get("INSTANCE")
        layer_details["database"] = connection_properties.get("DATABASE")

    # TODO: Implement details for web service layer


def _native_describe_fields(layer_or_table_fields):
    import ESRI.ArcGIS.Geodatabase as esriGeoDatabase

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

    try:
        fields = [{
            "field": _ao.cast_obj(layer_or_table_fields.get_Field(i), esriGeoDatabase.IField2),
            "fieldInfo": _ao.cast_obj(layer_or_table_fields.get_FieldInfo(i), esriGeoDatabase.IFieldInfo),
            "index": i
        } for i in range(0, layer_or_table_fields.FieldCount)]

        return [{
            "alias": f["fieldInfo"].Alias,
            "index": f["index"],
            "name": f["field"].Name,
            "type": field_type_id_to_name(f["field"].Type),
            "visible": f["fieldInfo"].Visible
        } for f in fields]
    except System.Runtime.InteropServices.COMException:
        # ignore this, the layer is probably broken, return no fields information
        return None


def _native_describe_layer(layer_parts):
    # avoid boxing/unboxing issues
    # not sure if this is really necessary, but getting weird results without it
    layer_is_valid = layer_parts["layer"].Valid
    layer_is_visible = layer_parts["layer"].Visible
    layer_name = layer_parts["layer"].Name

    layer_details = {
        "dataSource": _native_get_data_source(layer_parts),
        "database": None,
        "datasetName": _native_get_dataset_name(layer_parts),
        "datasetType": _native_get_dataset_type(layer_parts["dataset"]),
        "definitionQuery": _native_get_definition_query(layer_parts["featureLayerDefinition"]),
        "fields": _native_describe_fields(layer_parts["layerFields"]),
        "index": layer_parts["index"],
        "isBroken": not layer_is_valid,
        "isFeatureLayer": bool(layer_parts["featureLayer"]),
        "isNetworkAnalystLayer": bool(layer_parts["networkAnalystLayer"]),
        "isRasterLayer": bool(layer_parts["rasterLayer"]),
        "isRasterizingLayer": None,  # not implemented yet
        "isServiceLayer": None,  # not implemented yet
        "isGroupLayer": not layer_parts["groupLayer"] == None,
        "longName": "\\".join(_native_get_layer_name_parts(layer_parts)),
        "name": layer_name,
        "server": None,
        "service": None,
        "serviceId": _native_get_service_layer_property_value(layer_parts["serverLayerExtensions"], "ServiceLayerID"),
        "userName": None,
        "visible": layer_is_visible
    }

    _native_add_data_connection_details(layer_parts["dataset"], layer_details)

    return layer_details


def _native_describe_map(map_document, map_frame):
    # make the map frame active before getting details about it.
    _native_make_map_frame_active_view(map_frame)

    map_desc = {
        "name": map_frame.Name,
        "spatialReference": _get_spatial_ref(_native_get_map_spatial_ref_code(map_document,
                                                                              map_frame)).exportToString(),
        "layers": [],
        "tables": []
    }

    # ensure we release the layers we get
    with _ao.ComReleaser() as com_releaser:
        for l in _native_list_layers(map_document, map_frame):
            for (k, v) in viewitems(l):
                # add each item to the COM releaser
                com_releaser.manage_lifetime(v)
            map_desc["layers"].append(_native_describe_layer(l))

        for t in _native_list_tables(map_document, map_frame):
            for (k, v) in viewitems(t):
                # add each item to the COM releaser
                com_releaser.manage_lifetime(v)
            map_desc["tables"].append(_native_describe_table(t))

    return map_desc


def _native_describe_table(table_parts):
    table_details = {
        "dataSource": _native_get_data_source(table_parts),
        "database": None,
        "datasetName": _native_get_dataset_name(table_parts),
        "datasetType": _native_get_dataset_type(table_parts["standaloneTableDataset"]),
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
    import ESRI.ArcGIS.Geodatabase as esriGeoDatabase

    path = None

    if layer_or_table.get("featureLayer"):
        # input is a feature layer

        if layer_or_table["featureLayer"].FeatureClass:
            feature_class_name = layer_or_table["dataset"].Name

            workspace = _ao.cast_obj(layer_or_table["dataset"].Workspace, esriGeoDatabase.IWorkspace)
            workspace_path = workspace.PathName

            feature_class = _ao.cast_obj(layer_or_table["featureLayer"].FeatureClass, esriGeoDatabase.IFeatureClass)

            # Test if feature dataset in use, NULL COM pointers return falsey
            if feature_class.FeatureDataset:
                feature_dataset = _ao.cast_obj(feature_class.FeatureDataset, esriGeoDatabase.IFeatureDataset)
                feature_dataset_name = feature_dataset.Name
                path = os.path.join(workspace_path, feature_dataset_name, feature_class_name)
            else:
                path = os.path.join(workspace_path, feature_class_name)
    elif layer_or_table.get("rasterLayer"):
        # input is a raster
        path = layer_or_table["rasterLayer"].FilePath

    elif layer_or_table.get("tableDataset"):
        # input is a standalone table
        table_name = layer_or_table["tableDataset"].Name
        workspace = _ao.cast_obj(layer_or_table["tableDataset"].Workspace, esriGeoDatabase.IWorkspace)
        workspace_path = workspace.PathName
        path = os.path.join(workspace_path, table_name)

    return path


def _native_get_dataset_name(layer_or_table):
    import ESRI.ArcGIS.esriSystem as esriSystem

    dataset_name = None

    if layer_or_table.get("featureLayer"):
        # should be gotten from dataset
        dataset_name = layer_or_table["dataset"].Name if layer_or_table["dataset"] is not None else None
    elif layer_or_table.get("table"):
        # should be gotten from tableDataset
        dataset_name = layer_or_table["tableDataset"].Name if layer_or_table["tableDataset"] is not None else None
    elif layer_or_table.get("rasterLayer"):
        # should be gotten from data layer interface
        if layer_or_table["dataLayer"] is not None:
            dataset_name = _ao.cast_obj(layer_or_table["dataLayer"].DataSourceName, esriSystem.IName).NameString

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
    # ServerProperties.GetAllProperties() returns two lists, names and values, so zip them and turn them into a dictionary
    import ESRI.ArcGIS.esriSystem as esriSystem

    layer_extensions_server_properties = []

    for sle in service_layer_extensions:
        if sle is None:
            continue

        property_set = _ao.cast_obj(sle.ServerProperties, esriSystem.IPropertySet)
        _, property_keys, property_values = property_set.GetAllProperties(None, None)
        if len(property_keys) > 0:
            properties = dict(zip(property_keys, property_values))
            layer_extensions_server_properties.append(properties)

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
    import ESRI.ArcGIS.Geodatabase as esriGeoDatabase
    import ESRI.ArcGIS.Carto as esriCarto
    import ESRI.ArcGIS.NetworkAnalyst as esriNetworkAnalyst

    # list of all layers that we'll be returning
    layers = []

    def build_layer_parts(map_layer):
        layer_parts = {
            "children": [],
            "dataset": None,
            "dataLayer": _ao.cast_obj(map_layer, esriCarto.IDataLayer2),
            "layer": _ao.cast_obj(map_layer, esriCarto.ILayer2),
            "layerFields": _ao.cast_obj(map_layer, esriCarto.ILayerFields),
            "featureLayer": _ao.cast_obj(map_layer, esriCarto.IFeatureLayer),
            "featureLayerDefinition": _ao.cast_obj(map_layer, esriCarto.IFeatureLayerDefinition2),
            "groupLayer": _ao.cast_obj(map_layer, esriCarto.IGroupLayer),
            "index": len(layers),  # map index will be the same as the current length of this array
            "imageServerLayer": _ao.cast_obj(map_layer, esriCarto.IImageServerLayer),
            "mapServerLayer": _ao.cast_obj(map_layer, esriCarto.IMapServerLayer),
            "networkAnalystLayer": _ao.cast_obj(map_layer, esriNetworkAnalyst.INALayer),
            "parent": None,
            "rasterLayer": _ao.cast_obj(map_layer, esriCarto.IRasterLayer),
            "serverLayerExtensions": None
        }

        # get the relevant dataset
        dataset = None
        if bool(layer_parts["featureLayer"]):
            dataset = _ao.cast_obj(layer_parts["featureLayer"].FeatureClass, esriGeoDatabase.IDataset)
        elif bool(layer_parts["rasterLayer"]):
            dataset = _ao.cast_obj(layer_parts["rasterLayer"], esriGeoDatabase.IDataset)

        if not dataset is None:
            layer_parts["dataset"] = dataset

        # Get server layer extensions
        layer_extensions = _ao.cast_obj(map_layer, esriCarto.ILayerExtensions)
        layer_parts["serverLayerExtensions"] = [
            sle for sle in (_ao.cast_obj(layer_extensions.get_Extension(i), esriCarto.IServerLayerExtension)
                            for i in range(0, layer_extensions.get_ExtensionCount())) if sle is not None
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
            child_layer = _ao.cast_obj(composite_layer.get_Layer(i), esriCarto.ILayer2)

            # get child layer parts
            child_layer_parts = build_layer_parts(child_layer)

            # add child_layer_parts to the list of children for the current layer
            layer_parts["children"].append(child_layer_parts)

            # recursively find children
            get_child_layers(child_layer_parts, layer_parts)

    # iterate through the top level of layers
    map_layer_iterator = map_frame.get_Layers(None, False)
    map_layer_iterator = _ao.cast_obj(map_layer_iterator, esriCarto.IEnumLayer)
    map_layer = map_layer_iterator.Next()
    while (map_layer):
        layer_parts = build_layer_parts(map_layer)
        get_child_layers(layer_parts, None)

        map_layer = map_layer_iterator.Next()

    return layers


def _native_list_maps(map_document):
    """Gets a list of IMaps (Data Frames) from the provided map document."""

    # get the ArcObjects types we need
    import ESRI.ArcGIS.Carto as esriCarto

    # make sure map document is a map document
    map_document = _ao.cast_obj(map_document, esriCarto.IMapDocument)

    # iterate the list of maps, casting each one to IMap
    return [_ao.cast_obj(map_document.get_Map(i), esriCarto.IMap) for i in range(0, map_document.MapCount)]


def _native_list_tables(map_document, map_frame):
    """Iterates through a map frame to get all tables."""

    # get the ArcObjects types we need
    import ESRI.ArcGIS.Carto as esriCarto
    import ESRI.ArcGIS.Geodatabase as esriGeoDatabase

    # list of all tables
    tables = []

    def build_table_parts(standalone_table):
        table_parts = {
            "dataLayer": _ao.cast_obj(standalone_table, esriCarto.IDataLayer2),
            "index": len(tables),  # map index will be the same as the current length of this array
            "standaloneTable": standalone_table,
            "standaloneTableDataset": _ao.cast_obj(standalone_table, esriGeoDatabase.IDataset),
            "standaloneTableDefinition": _ao.cast_obj(standalone_table, esriCarto.ITableDefinition),
            "standaloneTableFields": _ao.cast_obj(standalone_table, esriGeoDatabase.ITableFields),
            "table": _ao.cast_obj(standalone_table.Table, esriGeoDatabase.ITable),
            "tableDataset": _ao.cast_obj(standalone_table.Table, esriGeoDatabase.IDataset),
            "serverLayerExtensions": None
        }

        # Get server layer extensions
        table_extensions = _ao.cast_obj(standalone_table, esriCarto.ITableExtensions)
        table_parts["serverLayerExtensions"] = [
            sle for sle in (_ao.cast_obj(table_extensions.get_Extension(i), esriCarto.IServerLayerExtension)
                            for i in range(0, table_extensions.get_ExtensionCount())) if sle is not None
        ]

        tables.append(table_parts)

        return table_parts

    # cast map to a standalone table collection to get access to tables
    table_collection = _ao.cast_obj(map_frame, esriCarto.IStandaloneTableCollection)

    # iterate the table collection
    for i in range(0, table_collection.StandaloneTableCount):
        table = _ao.cast_obj(table_collection.get_StandaloneTable(i), esriCarto.IStandaloneTable)
        build_table_parts(table)

    return tables


def _native_get_map_spatial_ref_code(map_document, map_frame):
    import ESRI.ArcGIS.Geometry as esriGeometry

    with _ao.ComReleaser() as com_releaser:
        sr = _ao.cast_obj(map_frame.SpatialReference, esriGeometry.ISpatialReference)
        com_releaser.manage_lifetime(sr)
        factory_code = sr.FactoryCode
        return factory_code


def _native_mxd_exists(mxd_path):
    import ESRI.ArcGIS.Carto as esriCarto

    logger = _get_logger()
    logger.debug("Checking if MXD exists: %s", mxd_path)

    with _ao.ComReleaser() as com_releaser:
        map_document = _ao.create_obj(esriCarto.MapDocument, esriCarto.IMapDocument)
        com_releaser.manage_lifetime(map_document)
        exists = map_document.get_IsPresent(mxd_path)
        valid = map_document.get_IsMapDocument(mxd_path)
        return exists and valid


def _native_document_close(map_document):
    import ESRI.ArcGIS.Carto as esriCarto

    # Make sure it's a map document
    map_document = _ao.cast_obj(map_document, esriCarto.IMapDocument)
    map_document.Close()


def _native_document_open(mxd_path):
    #import comtypes.gen.esriCarto as esriCarto
    import ESRI.ArcGIS.Carto as esriCarto

    if _native_mxd_exists(mxd_path):
        map_document = _ao.create_obj(esriCarto.MapDocument, esriCarto.IMapDocument)
        map_document.Open(mxd_path)

        # Maps must be activated in order for all properties to be initialized correctly
        maps = _native_list_maps(map_document)
        for m in maps:
            _native_make_map_frame_active_view(m)

        return map_document
    else:
        raise ValueError("MXD path '{}' not found or document invalid.".format(str(mxd_path)))


def _native_make_map_frame_active_view(map_frame):
    import ESRI.ArcGIS.Carto as esriCarto

    window_handle = ctypes.windll.user32.GetDesktopWindow()

    # cast map frame to active view
    active_view = _ao.cast_obj(map_frame, esriCarto.IActiveView)

    # make it the active view
    active_view.Activate(window_handle)


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
