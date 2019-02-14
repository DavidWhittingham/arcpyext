import logging
import re
from itertools import zip_longest

import arcpy

from ..exceptions import MapLayerError, DataSourceUpdateError, UnsupportedLayerError, ChangeDataSourcesError
from ..arcobjects import init_arcobjects_context, destroy_arcobjects_context, list_layers

# Configure module logging
logger = logging.getLogger("arcpyext.mapping")

def list_document_data_sources(project):
    """List the data sources for each layer or table view of the specified map.

    Outputs a dictionary containing two keys, "layers" and "tableViews".

    "layers" contains an array, with each element representing a data frame (as another array) that contains a
    dictionary of layer details relevant to that layer's connection to its data source.

    "tableViews" is also an array, where each element is a dictionary of table view details relevant to that table
    view's connection to its data source.

    The order of array elements is as displayed in the ArcMap table of contents.

    An example of the output format is the following::

        {
            "layers": [
                [
                    # Data frame number one
                    {
                        # Layer number one
                        "id":               "Layer ID",
                        "name":             "Layer Name",
                        "longName":         "Layer Group/Layer Name",
                        "datasetName":      "(Optional) dataset name",
                        "dataSource":       "(Optional) data source name",
                        "serviceType":      "(Optional) service type, e.g. SDE, MapServer, IMS",
                        "userName":         "(Optional) user name",
                        "server":           "(Optional) server address/hostname",
                        "service":          "(Optional) name or number of the ArcSDE Service",
                        "database":         "(Optional) name of the database",
                        "workspacePath":    "(Optional) workspace path"
                        "visible":          "(Optional) visibility"
                        "definitionQuery":  "definition query on the layer"
                    },
                    # ...more layers
                ],
                # ...more data frames
            ],
            "tableViews": [
                {
                    "datasetName":          "dataset name",
                    "dataSource":           "data source",
                    "definitionQuery":      "definition query on the table",
                    "workspacePath":        "workspace path"
                }
            ]
        }

    :param map: The map to gather data source connection details about
    :type map: arcpy.mapping.MapDocument
    :returns: dict

    
    layers = []
    tableViews = []
    for map in project.listMaps():
        layers.append([_get_layer_details(layer) for layer in map.listLayers()])
        tableViews.append([_get_table_details(table) for table in map.listTables()])"""

    layers = [[_get_layer_details(layer) for layer in df.listLayers()] for df in project.listMaps()]
    tableViews = [[_get_table_details(table) for table in df.listTables()] for df in project.listMaps()]
    # Enrich arcpy data with additional information that is only accessible via arcobjects
    try:

        init_arcobjects_context()
        additional_layer_info = list_layers(map.filePath)
        destroy_arcobjects_context()

        for layerGroup in layers:
            for l in layerGroup:
                if l is not None:
                    layerName = l['name']
                    layer_info = additional_layer_info[layerName]
                    if layer_info is not None:
                        l["id"] = layer_info['id']
                        l["hasFixedId"] = layer_info['hasFixedId']
                        l["visible"] = layer_info['visible']
                        l["definitionQuery"] = layer_info['definitionQuery']



    except Exception as e:
        logger.exception("Could not read additional layer info using arcobjects")

    return {
        "layers": layers,
        "tableViews": tableViews
    }

def _get_layer_details(layer):
    if layer.isGroupLayer and not layer.isNetworkAnalystLayer:
        return None

    details = {
        "name": layer.name,
        "longName": layer.longName
    }

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
    except Exception as e:
        logger.exception("Could not resolve layer fields ({0}). The layer datasource may be broken".format(layer.name))

    return details

def _get_table_details(table):
    return {
        "connectionProperties": table.connectionProperties,
        "dataSource": table.dataSource,
        "definitionQuery": table.definitionQuery,
        "name": table.name
    }
