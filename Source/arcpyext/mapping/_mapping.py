import re
import os
from itertools import izip_longest

import arcpy

from ..exceptions import MapLayerError, DataSourceUpdateError, UnmappedDataSourceError, UnsupportedLayerError, \
    ChangeDataSourcesError, MapDataSourcesBrokenError, ServDefDraftCreateError

from _sddraft import SDDraft

def change_data_sources(map, data_sources):
    """ """
    errors = []
    data_tables = arcpy.mapping.ListTableViews(map)
    layers_by_df = [arcpy.mapping.ListLayers(df) for df in arcpy.mapping.ListDataFrames(map)]
    
    if not 'layers' in data_sources or not 'tableViews' in data_sources:
        raise ChangeDataSourcesError("Data sources dictionary does not contain both 'layers' and 'tableViews' keys")
    
    for layers, layer_sources in izip_longest(layers_by_df, data_sources["layers"]):
        
        if layer_sources == None or len(layers) != len(layer_sources):
            raise ChangeDataSourcesError("Number of layers does not match number of data sources.")

        for layer, layer_source in izip_longest(layers, layer_sources):
            try:
                if layer.isGroupLayer or layer_source == None:
                    continue

                if not layer.supports("dataSource") or not layer.supports("workspacePath"):
                    #error on layers that we can't change
                    raise UnsupportedLayerError(layer = layer)


                if layer.supports("dataSource"):
                    print(u"Layer '{0}': Current datasource: '{1}'".format(layer.longName, layer.dataSource).encode("ascii", "ignore"))

                print(u"Layer '{0}': Attempting to change workspace path".format(layer.longName).encode("ascii", "ignore"))
                _change_data_source(layer, layer_source["workspacePath"], layer_source.get("datasetName"), layer_source.get("workspaceType"), layer_source.get("schema"))
                print(u"Layer '{0}': Workspace path updated to: '{1}'".format(layer.name, layer_source["workspacePath"]).encode("ascii", "ignore"))

                if layer.supports("dataSource"):
                    print(u"Layer '{0}': New datasource: '{1}'".format(layer.longName, layer.dataSource).encode("ascii", "ignore"))

            except MapLayerError as mle:
                errors.append(mle)

    if not len(data_tables) == len(data_sources['tableViews']):
        raise ChangeDataSourcesError("Number of data tables does not match number of data table data sources.")

    for data_table, layer_source in izip_longest(data_tables, data_sources['tableViews']):
        try:
            if layer_source == None:
                continue

            print(u"Data Table '{0}': Attempting to change workspace path".format(data_table.name).encode("ascii", "ignore"))
            _change_data_source(data_table, layer_source["workspacePath"], layer_source.get("datasetName"), layer_source.get("workspaceType"), layer_source.get("schema"))
            print(u"Data Table '{0}': Workspace path updated to: '{1}'".format(data_table.name, layer_source["workspacePath"]).encode("ascii", "ignore"))

        except MapLayerError as mle:
            errors.append(mle)

    if not len(errors) == 0:
        raise ChangeDataSourcesError("A number of errors were encountered whilst change layer data sources.", errors)
        
def create_replacement_data_sources_list(document_data_sources_list, data_source_templates, raise_exception_no_change = False):
    template_sets = [dict(template.items() + [("matchCriteria", set(template["matchCriteria"].items()))]) for template in data_source_templates]
    
    def match_new_data_source(item):
        if item == None:
            return None
            
        new_conn = None
        for template in template_sets:
            if template["matchCriteria"].issubset(set(item.items())):
                new_conn = template["dataSource"]
                break
        if new_conn == None and raise_exception_no_change:
            raise RuntimeError("No matching data source was found for layer")
        return new_conn
    
    return {
        "layers": [[match_new_data_source(layer) for layer in df] for df in document_data_sources_list["layers"]],
        "tableViews": [match_new_data_source(table) for table in document_data_sources_list["tableViews"]]
    }

def convert_map_to_service_draft(map, sd_draft_path, service_name, folder_name = None, summary = None):

    def check_analysis(analysis):
        if not analysis["errors"] == {}:
            err_message_list = []
            for ((message, code), layerlist) in analysis["errors"].iteritems():
                if layerlist == None:
                    err_message_list.append("{message} (CODE {code})".format(message = message, code = code))
                else:
                    err_message_list.append("{message} (CODE {code}) applies to: {layers}".format(
                                                message = message, code = code, layers = ", ".join([layer.name for layer in layerlist])))
            raise ServDefDraftCreateError("Analysis Errors: \n{errs}".format(errs = "\n".join(err_message_list)))

    if not validate_map(map):
        raise MapDataSourcesBrokenError()

    if os.path.exists(sd_draft_path):
        os.remove(sd_draft_path)

    analysis = arcpy.mapping.CreateMapSDDraft(map, sd_draft_path, service_name, server_type = "ARCGIS_SERVER", 
                                   copy_data_to_server = False, folder_name = folder_name, summary = summary)
    check_analysis(analysis)

    analysis = arcpy.mapping.AnalyzeForSD(sd_draft_path)
    check_analysis(analysis)

    return SDDraft(sd_draft_path)

def convert_service_draft_to_staged_service(sd_draft, sd_path):
    if os.path.exists(sd_path):
        os.remove(sd_path)

    if isinstance(sd_draft, basestring):
        arcpy.StageService_server(sd_draft, sd_path)
    else:
        arcpy.StageService_server(sd_draft.file_path, sd_path)
        
def list_document_data_sources(map):
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
                        "name":          "Layer Name",
                        "longName":      "Layer Group/Layer Name",
                        "datasetName":   "(Optional) dataset name",
                        "dataSource":    "(Optional) data source name",
                        "serviceType":   "(Optional) service type, e.g. SDE, MapServer, IMS",
                        "userName":      "(Optional) user name",
                        "server":        "(Optional) server address/hostname",
                        "service":       "(Optional) name or number of the ArcSDE Service",
                        "database":      "(Optional) name of the database",
                        "workspacePath": "(Optional) workspace path"
                    },
                    # ...more layers
                ],
                # ...more data frames
            ],
            "tableViews": [
                {
                    "datasetName": "dataset name",
                    "dataSource": "data source",
                    "definitionQuery": "definition query on the table",
                    "workspacePath": "workspace path"
                }
            ]
        }
    
    :param map: The map to gather data source connection details about
    :type map: arcpy.mapping.MapDocument
    :returns: dict
    
    """
    
    return {
        "layers": [[_get_layer_details(layer) for layer in arcpy.mapping.ListLayers(df)] for df in arcpy.mapping.ListDataFrames(map)],
        "tableViews": [_get_table_details(table) for table in arcpy.mapping.ListTableViews(map)]
    }
        
def validate_map(map):
    """Analyse the map for broken layers and return a boolean indicating if it is in a valid state or not.
    
    Lists broken layers on the shell output.
    
    :param map: The map to be validated
    :type map: arcpy.mapping.MapDocument
    :returns: Boolean, True if valid, False if there are one or more broken layers
    
    """
    
    broken_layers = arcpy.mapping.ListBrokenDataSources(map)

    if len(broken_layers) > 0:
        print(u"Map '{0}': Broken data sources:".format(map.title))
        for layer in broken_layers:
            print(u" {0}".format(layer.name))
            if layer.supports("workspacePath"):
                print(u"  workspace: {0}".format(layer.workspacePath))
            if layer.supports("dataSource"):
                print(u"  datasource: {0}".format(layer.dataSource))
        
        return False
        
    return True
        
def _change_data_source(layer, workspace_path, dataset_name = None, workspace_type = None, schema = None):
    try:
        if ((not hasattr(layer, "supports") or layer.supports("workspacePath")) and
            (dataset_name == None and workspace_type == None and schema == None)):

            # Tests if layer is actually a layer object (i.e. has a "support" function) or table view (which doesn't, 
            # but always supports "workspacePath").  Can't test on type (arcpy.mapping.TableView) as that doesn't work 
            # on ArcPy 10.0

            layer.findAndReplaceWorkspacePath("", workspace_path, validate = False)
            return
            
        kwargs = { "validate": False }

        if dataset_name == None and hasattr(layer, "supports") and layer.supports("datasetName"):
            if layer.supports("workspacePath"):
                dataset_name = layer.dataSource.replace(layer.workspacePath, "")
            else:
                dataset_name = layer.datasetName
        
        if dataset_name != None:
            if (schema != None):
                ds_user, ds_name, fc_user, fc_name = _parse_data_source(dataset_name)
                
                dataset_name = "{0}.{1}".format(schema, fc_name)

            kwargs["dataset_name"] = dataset_name
            
        if workspace_type != None:
            kwargs["workspace_type"] = workspace_type
            
        layer.replaceDataSource(workspace_path, **kwargs)
        
    except Exception, e:
        raise DataSourceUpdateError("Exception raised internally by ArcPy", layer, e)
    
    if hasattr(layer, "isBroken") and layer.isBroken:
        raise DataSourceUpdateError("Layer is now broken.", layer)

        
def _get_layer_details(layer):
    if layer.isGroupLayer:
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
        details["userName"] = layer.serviceProperties["UserName"]
        
        if layer.serviceProperties["ServiceType"].upper() == "SDE":
            details["server"] = layer.serviceProperties["Server"]
            details["service"] = layer.serviceProperties["Service"]
            details["database"] = layer.serviceProperties["Database"]
    
    if layer.supports("workspacePath"):
        details["workspacePath"] = layer.workspacePath
        
    return details
        
def _get_table_details(table):
    return {
        "datasetName": table.datasetName,
        "dataSource": table.dataSource,
        "definitionQuery": table.definitionQuery,
        "workspacePath": table.workspacePath
    }

def _parse_data_source(data_source):
    """Takes a string describing a data source and returns a four-part tuple describing the dataset username, dataset 
    name, feature class username and feature class name"""

    dataset_regex = re.compile(
                        r"^(?:\\)?(?P<ds_user>[\w]*?)(?:\.)?(?P<ds_name>[\w]*?(?=\\))(?:\\)?(?P<fc_user>[\w]*?(?=\.))(?:\.)(?P<fc_name>[\w]*?)$",
                        re.IGNORECASE)

    r = dataset_regex.search(data_source)

    if r == None:
        feature_class_regex = re.compile(
                                r"^(?:\\)?(?P<fc_user>[\w]*?(?=\.))(?:\.)(?P<fc_name>[\w]*?)$",
                                re.IGNORECASE)
        r = feature_class_regex.search(data_source)

    if r == None:
        return (None, None, None, data_source)

    r = r.groupdict()

    return (r.get("ds_user"), r.get("ds_name"), r.get("fc_user"), r.get("fc_name"))