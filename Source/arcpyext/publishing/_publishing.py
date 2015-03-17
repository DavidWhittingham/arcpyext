import os

import arcpy

from ..exceptions import MapDataSourcesBrokenError, ServDefDraftCreateError
from ..mapping import validate_map

from ._mapsddraft import MapSDDraft

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

    return MapSDDraft(sd_draft_path)

def convert_service_draft_to_staged_service(sd_draft, sd_path):
    if os.path.exists(sd_path):
        os.remove(sd_path)

    if isinstance(sd_draft, basestring):
        arcpy.StageService_server(sd_draft, sd_path)
    else:
        arcpy.StageService_server(sd_draft.file_path, sd_path)