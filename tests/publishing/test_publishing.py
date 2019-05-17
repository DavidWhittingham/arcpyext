import arcpyext
import os
import sys

PROJECT_PATH = os.path.abspath("{0}/../samples/ChemicalDistributionRegulatedAreas.aprx".format(os.path.dirname(__file__)))
MXD_PATH = os.path.abspath("{0}/../samples/test_mapping.mxd".format(os.path.dirname(__file__)))
DRAFT_PATH = os.path.abspath("{0}/../samples/test_mapping.sddraft".format(os.path.dirname(__file__)))


def test_convert_map_to_sddraft():
    if sys.version_info.major > 2:
        mapservice = arcpyext.publishing.convert_map_to_service_draft(
            PROJECT_PATH,
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
                                                                      copy_data_to_server=False)

    assert os.path.exists(mapservice)