# Python 2/3 compatibility
# pylint: disable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position,no-name-in-module,import-error
from __future__ import (absolute_import, division, print_function, unicode_literals)
from future.builtins.disabled import *
from future.builtins import *
from future.standard_library import install_aliases
install_aliases()
# pylint: enable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position,no-name-in-module,import-error

# Standard lib imports
import os
import sys

# Third-party imports
import pytest

# Local imports
import arcpyext
from arcpyext.exceptions.serv_def_draft_create_error import ServDefDraftCreateError
from arcpyext.publishing._publishing import check_analysis

PROJECT_PATH = os.path.abspath("{0}/../samples/test_mapping_complex.aprx".format(os.path.dirname(__file__)))
MXD_PATH = os.path.abspath("{0}/../samples/test_mapping_complex.mxd".format(os.path.dirname(__file__)))
DRAFT_PATH = os.path.abspath("{0}/../samples/test_mapping_complex.sddraft".format(os.path.dirname(__file__)))


def test_convert_map_to_sddraft():
    if sys.version_info.major > 2:
        mapservice = arcpyext.publishing.convert_map_to_service_draft(
            PROJECT_PATH, DRAFT_PATH, 'Test', 'Test', copy_data_to_server=False, portal_folder=None
        )
    else:
        mapservice = arcpyext.publishing.convert_map_to_service_draft(
            MXD_PATH, DRAFT_PATH, 'Test', 'Test', copy_data_to_server=False
        )

    assert os.path.exists(mapservice)


@pytest.mark.skipif(sys.version_info >= (3, 0), reason="requires Python 2")
def test_check_analysis():
    with pytest.raises(ServDefDraftCreateError):
        arcpyext.publishing._publishing.check_analysis(
            {
                "messages": None,
                "warnings": None,
                "errors": {
                    ('Some message', 999): None
                }
            }
        )
