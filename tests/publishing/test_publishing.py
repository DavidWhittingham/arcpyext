import arcpyext
import agsconfig
from os import path
import sys

PROJECT_PATH = path.abspath("{0}/../samples/ChemicalDistributionRegulatedAreas.aprx".format(path.dirname(__file__)))
MXD_PATH = path.abspath("{0}/../samples/test_mapping.mxd".format(path.dirname(__file__)))
DRAFT_PATH = path.abspath("C:/temp/test.sddraft")

def test_convert_project_to_sddraft():
    if sys.version_info.major > 2:
        mapservice = arcpyext.publishing.convert_map_to_service_draft(PROJECT_PATH, 
                                                            DRAFT_PATH, 
                                                            'Test', 
                                                            'Test', 
                                                            copy_data_to_server=False, 
                                                            server='https://uat-spatial.information.qld.gov.au', 
                                                            portal_folder=None)
    else:
        mapservice = arcpyext.publishing.convert_map_to_service_draft(MXD_PATH, 
                                                    DRAFT_PATH, 
                                                    'Test', 
                                                    'Test', 
                                                    copy_data_to_server=False, 
                                                    server='https://uat-spatial.information.qld.gov.au', 
                                                    portal_folder=None)
        
    assert isinstance(mapservice, agsconfig.services.map_server.MapServer)