import os.path
import shutil

import arcpyext
import pytest

from arcpyext.publishing._geodata_sddraft import GeodataSDDraft
from arcpyext.publishing._sddraft_editor import SDDraftEditor
from .. helpers import *

SDDRAFT_FILE_PATH = os.path.abspath("{0}/../samples/geodataservice.sddraft".format(os.path.dirname(__file__)))
SDDRAFT_FILE_PATH_COPY = os.path.abspath("{0}/../samples/geodataservice.copy.sddraft".format(os.path.dirname(__file__)))
SDDRAFT_SAVE_TEST_FILE_PATH = os.path.abspath("{0}/../samples/geodataservice.savetest.sddraft".format(os.path.dirname(__file__)))

@pytest.fixture
def sddraft():
    shutil.copyfile(SDDRAFT_FILE_PATH, SDDRAFT_FILE_PATH_COPY)
    return GeodataSDDraft(SDDraftEditor(SDDRAFT_FILE_PATH_COPY))

from sddraftbase import *

@pytest.mark.parametrize(("capabilities", "expected", "ex"), [
    ([GeodataSDDraft.Capability.query], [GeodataSDDraft.Capability.query], None),
    ([], [GeodataSDDraft.Capability.query], None),
    (["Replication"], [GeodataSDDraft.Capability.query, GeodataSDDraft.Capability.replication], None),
    (["Fail"], None, ValueError),
    ([123], None, TypeError)
])
def test_capabilities(sddraft, capabilities, expected, ex):
    if ex != None:
        with pytest.raises(ex):
            sddraft.capabilities = capabilities
    else:
        sddraft.capabilities = capabilities
        assert set(sddraft.capabilities) == set(expected)