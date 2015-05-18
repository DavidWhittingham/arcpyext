import os.path
import shutil

import arcpyext
import pytest

from arcpyext.publishing import GPSDDraft
from arcpyext.publishing import SDDraftEditor
from .. helpers import *

SDDRAFT_FILE_PATH = os.path.abspath("{0}/../samples/pythongpservice.sddraft".format(os.path.dirname(__file__)))
SDDRAFT_FILE_PATH_COPY = os.path.abspath("{0}/../samples/pythongpservice.copy.sddraft".format(os.path.dirname(__file__)))
SDDRAFT_SAVE_TEST_FILE_PATH = os.path.abspath("{0}/../samples/pythongpservice.savetest.sddraft".format(os.path.dirname(__file__)))

@pytest.fixture
def sddraft():
    shutil.copyfile(SDDRAFT_FILE_PATH, SDDRAFT_FILE_PATH_COPY)
    return GPSDDraft(SDDraftEditor(SDDRAFT_FILE_PATH_COPY))

from sddraftbase import *

@pytest.mark.parametrize(("capabilities", "expected", "ex"), [
    ([GPSDDraft.Capability.uploads], [GPSDDraft.Capability.uploads], None),
    ([], [], None),
    (["Uploads"], [GPSDDraft.Capability.uploads], None),
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

@pytest.mark.parametrize(("type", "expected", "ex"), [
    (GPSDDraft.ExecutionType.synchronous, GPSDDraft.ExecutionType.synchronous, None),
    (GPSDDraft.ExecutionType.asynchronous, GPSDDraft.ExecutionType.asynchronous, None),
    ("Synchronous", GPSDDraft.ExecutionType.synchronous, None),
    ("Asynchronous", GPSDDraft.ExecutionType.asynchronous, None),
    ("Fail", None, ValueError)
])
def test_execution_type(sddraft, type, expected, ex):
    if ex != None:
        with pytest.raises(ex):
            sddraft.execution_type = type
    else:
        sddraft.execution_type = type
        assert sddraft.execution_type == expected

@pytest.mark.parametrize(("enabled", "expected"), TRUEISH_TEST_PARAMS)
def test_result_map_server(sddraft, enabled, expected):
    sddraft.result_map_server = enabled
    assert sddraft.result_map_server == expected

@pytest.mark.parametrize(("message_level", "expected", "ex"), [
    ("None", GPSDDraft.MessageLevel.none, None),
    (GPSDDraft.MessageLevel.error, GPSDDraft.MessageLevel.error, None),
    ("Fail", None, ValueError)
])
def test_show_messages(sddraft, message_level, expected, ex):
    if ex != None:
        with pytest.raises(ex):
            sddraft.show_messages = message_level
    else:
        sddraft.show_messages = message_level
        assert sddraft.show_messages == expected