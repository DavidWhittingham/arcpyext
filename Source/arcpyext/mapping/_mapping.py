import re
import os
from itertools import izip_longest

import arcpy

from ..exceptions import MapLayerError, DataSourceUpdateError, UnmappedDataSourceError, UnsupportedLayerError, \
    ChangeDataSourcesError, MapDataSourcesBrokenError, ServDefDraftCreateError

from _sddraft import SDDraft

def split_arc_data_path(file_path):
    shp_re = re.search("(^.+)(\.shp\Z)", file_path)
    if not shp_re == None:
        file_path = os.path.normpath(file_path)
        return (os.path.dirname(file_path), os.path.splitext(os.path.split(file_path)[1])[0])

    return (file_path, None)

def change_data_source(layer, new_workspace, out_schema):
    """ Changes the data source of a layer or data table """

    try:
        # this fails with shape files and possibly other data source type, but there seems to be no good way
        # of knowing up front if it will fail
        layer.findAndReplaceWorkspacePath("", new_workspace)
    except:
        # this won't work with query layers, but those do work with the previous statement.
        (new_workspace, new_dataset_name) = split_arc_data_path(new_workspace)
        print("change_data_source: workspace {0}  dataset_name {1}".format(new_workspace, new_dataset_name))
        if not new_dataset_name == None:
            layer.replaceDataSource(new_workspace, dataset_name = new_dataset_name)
        else:
            dataset_name = None
            if layer.supports("datasetName") and out_schema is not None:
                match = re.search("^(.*)\.(.*)\.(.*)$", layer.datasetName)
                if match is not None:
                    featureclass_name = match.group(3)
                    dataset_name = "{0}.{1}".format(out_schema, featureclass_name)
                    
            
            if dataset_name is not None:
                layer.replaceDataSource(new_workspace, dataset_name = dataset_name)
            else:
                layer.replaceDataSource(new_workspace)

    if layer.workspacePath != new_workspace:
        raise DataSourceUpdateError(layer = layer)


def change_data_sources(map, data_sources):
    """ """
    errors = []
    data_tables = arcpy.mapping.ListTableViews(map)
    layers = arcpy.mapping.ListLayers(map)

    if not 'layers' in data_sources or not 'dataTables' in data_sources:
        raise ChangeDataSourcesError("Data sources dictionary does not contain both 'layers' and 'dataTables' keys")

    layer_sources = data_sources['layers']
    
    if not len(layers) == len(layer_sources):
        raise ChangeDataSourcesError("Number of layers does not match number of data sources.")

    for layer, layer_source in izip_longest(layers, layer_sources):
        try:
            if layer.isGroupLayer or layer_source == None:
                continue

            if not layer.supports("dataSource") or not layer.supports("workspacePath"):
                #error on layers that we can't change
                raise UnsupportedLayerError(layer = layer)


            if layer.supports("dataSource"):
                print("Layer '{0}': Current datasource: '{1}'".format(layer.longName, layer.dataSource))

            print("Layer '{0}': Attempting to change workspace path".format(layer.longName))
            change_data_source(layer, layer_source["workspace"], layer_source.get("outSchema"))
            print("Layer '{0}': Workspace path updated to: '{1}'".format(layer.name, layer_source["workspace"]))

            if layer.supports("dataSource"):
                print("Layer '{0}': New datasource: '{1}'".format(layer.longName, layer.dataSource))

        except MapLayerError as mle:
            errors.append(mle)
    
    data_table_sources = data_sources['dataTables']

    if not len(data_tables) == len(data_table_sources):
        raise ChangeDataSourcesError("Number of data tables does not match number of data table data sources.")

    for data_table, layer_source in izip_longest(data_tables, data_table_sources):
        try:
            if layer_source == None:
                continue

            print("Data Table '{0}': Attempting to change workspace path".format(data_table.name))
            change_data_source(data_table, layer_source["workspace"], layer_source.get("outSchema"))
            print("Data Table '{0}': Workspace path updated to: '{1}'".format(data_table.name, layer_source["workspace"]))

        except MapLayerError as mle:
            errors.append(mle)


    if not len(errors) == 0:
        raise ChangeDataSourcesError(errors = errors)

def validate_map(map):
    broken_layers = arcpy.mapping.ListBrokenDataSources(map)

    if len(broken_layers) > 0:
        print "Map '{0}': Broken data sources:".format(map.title)
        for layer in broken_layers:
            print(" {0}".format(layer.name))
            if layer.supports("workspacePath"):
                print("  workspace: {0}".format(layer.workspacePath))
            if layer.supports("dataSource"):
                print("  datasource: {0}".format(layer.dataSource))

    return len(broken_layers) == 0

def convert_map_to_service_draft(map, sd_draft_path, service_name, folder_name = None, summary = None):

    def check_analysis(analysis):
        if not analysis["errors"] == {}:
            err_message_list = []
            for ((message, code), layerlist) in analysis["errors"].iteritems():
                if layerlist == None:
                    err_message_list.append("{message} (CODE {code})".format(message = message, code = code))
                else:
                    err_message_list.append("{message} (CODE {code}) applies to: {layers}".format(
                                                message = message, code = code, layers = ", ".join(layerlist)))
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