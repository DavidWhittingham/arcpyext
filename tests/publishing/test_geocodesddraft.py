from __future__ import (absolute_import, division, print_function, unicode_literals)
from builtins import (bytes, dict, int, list, object, range, str, ascii, chr, hex, input, next, oct, open, pow, round,
                      super, filter, map, zip)

import os.path
import shutil

import arcpyext
import pytest

from arcpyext.publishing._geocode_sddraft import GeocodeSDDraft
from .. helpers import *

SDDRAFT_FILE_PATH = os.path.abspath("{0}/../samples/geocodeservice.sddraft".format(os.path.dirname(__file__)))
SDDRAFT_FILE_PATH_COPY = os.path.abspath("{0}/../samples/geocodeservice.copy.sddraft".format(os.path.dirname(__file__)))
SDDRAFT_SAVE_TEST_FILE_PATH = os.path.abspath("{0}/../samples/geocodeservice.savetest.sddraft".format(os.path.dirname(__file__)))

@pytest.fixture
def sddraft():
    shutil.copyfile(SDDRAFT_FILE_PATH, SDDRAFT_FILE_PATH_COPY)
    return arcpyext.publishing.load_geocode_sddraft(SDDRAFT_FILE_PATH_COPY)

from .sddraftbase import *

@pytest.mark.parametrize(("capabilities", "expected", "ex"), [
    ([GeocodeSDDraft.Capability.geocode], [GeocodeSDDraft.Capability.geocode], None),
    ([], [], None),
    (["Geocode"], [GeocodeSDDraft.Capability.geocode], None),
    (["Fail"], None, ValueError),
    ([123], None, TypeError)
])
def test_capabilities(sddraft, capabilities, expected, ex):
    assert isinstance(type(sddraft).capabilities, property) == True
    if ex != None:
        with pytest.raises(ex):
            sddraft.capabilities = capabilities
    else:
        sddraft.capabilities = capabilities
        assert set(sddraft.capabilities) == set(expected)

def test_save(sddraft):
    sddraft.save()
    assert True

@pytest.mark.parametrize(("output"), [
    (SDDRAFT_SAVE_TEST_FILE_PATH)
])
def test_save_a_copy(sddraft, output):
    sddraft.save_a_copy(output)
    assert os.path.isfile(output) == True