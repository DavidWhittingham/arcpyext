# Python 2/3 compatibility
from __future__ import (absolute_import, division, print_function, unicode_literals)
from future.builtins import *
from future.builtins.disabled import *
from future.standard_library import install_aliases
install_aliases()

import os

import arcpy

from ..exceptions import MapDataSourcesBrokenError, ServDefDraftCreateError
from ..mapping import validate_map

import agsconfig

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

def convert_pro_project_to_service_draft(project, sd_draft_path, service_name, folder_name = None, summary = None, copy_data_to_server = False, server = None, portal_folder = None):
    from ..mp import validate_pro_project

    # Pro requires a ags url without /arcgis at the end
    server = server.replace('/arcgis', '')

    if type(project) == str:
        project = arcpy.mp.ArcGISProject(project)

    if not validate_pro_project(project):
        raise MapDataSourcesBrokenError("One or more layers have broken data sources.")

    if os.path.exists(sd_draft_path):
        os.remove(sd_draft_path)

    draft = arcpy.sharing.CreateSharingDraft('STANDALONE_SERVER', # This is a fixed value and doesn't do anything
                                                'MAP_SERVICE',
                                                service_name,
                                                project.listMaps()[0]) #TODO: Do something about using only the first map in the project

    if copy_data_to_server == 'false':
        draft.copyDataToServer = False
    elif copy_data_to_server == 'true':
        draft.copyDataToServer = True
        
    #draft.targetServer = server
    draft.offline = True
    draft.serverFolder = folder_name
    draft.portalFolder = portal_folder
    draft.exportToSDDraft(sd_draft_path)

    return load_map_sddraft(sd_draft_path)

def convert_map_to_service_draft(map, sd_draft_path, service_name, folder_name = None, summary = None, copy_data_to_server = False, server = None, portal_folder = None):
    # server and portal_folder parameters are required for pro services. Ignore in this function.
    if type(map) == str:
        map = arcpy.mapping.MapDocument(map)
    
    if not validate_map(map):
        raise MapDataSourcesBrokenError("One or more layers have broken data sources.")

    if os.path.exists(sd_draft_path):
        os.remove(sd_draft_path)

    analysis = arcpy.mapping.CreateMapSDDraft(
        map,
        sd_draft_path,
        service_name,
        server_type = "ARCGIS_SERVER",
        copy_data_to_server = copy_data_to_server,
        folder_name = folder_name,
        summary = summary)

    check_analysis(analysis)

    analysis = arcpy.mapping.AnalyzeForSD(sd_draft_path)
    check_analysis(analysis)

    return load_map_sddraft(sd_draft_path)

def convert_service_draft_to_staged_service(sd_draft, sd_path):
    if os.path.exists(sd_path):
        os.remove(sd_path)

    if isinstance(sd_draft, str):
        arcpy.StageService_server(sd_draft, sd_path)
    else:
        arcpy.StageService_server(sd_draft.file_path, sd_path)

def convert_toolbox_to_service_draft(toolbox_path, sd_draft_path, get_result_fn, service_name, folder_name = None, summary = None):
    # import and run the package
    arcpy.ImportToolbox(toolbox_path)
    # optionally allow a list of results
    if not callable(get_result_fn):
        result = [fn() for fn in get_result_fn]
    else:
        result = get_result_fn()

    # create the sddraft
    analysis = arcpy.CreateGPSDDraft(result, sd_draft_path, service_name, server_type="ARCGIS_SERVER",
                            copy_data_to_server=False, folder_name=folder_name, summary=summary)
    check_analysis(analysis)
    # and analyse it
    analysis = arcpy.mapping.AnalyzeForSD(sd_draft_path)
    check_analysis(analysis)

    return load_gp_sddraft(sd_draft_path)

def load_geocode_sddraft(path):
    with open(path, "rb+") as file:
        return agsconfig.load_geocode_sddraft(file)

def load_geodata_sddraft(path):
    raise NotImplementedError

def load_gp_sddraft(path):
    with open(path, "rb+") as file:
        return agsconfig.load_geoprocessing_sddraft(file)

def load_image_sddraft(path):
    with open(path, "rb+") as file:
        return agsconfig.load_image_sddraft(file)

def load_map_sddraft(path):
    with open(path, "rb+") as file:
        return agsconfig.load_map_sddraft(file)