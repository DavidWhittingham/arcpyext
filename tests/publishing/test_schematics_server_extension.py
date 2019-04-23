import os.path
import shutil

import arcpyext
import agsconfig
import pytest

from .. helpers import *

SDDRAFT_FILE_PATH = os.path.abspath("{0}/../samples/example.sddraft".format(os.path.dirname(__file__)))
SDDRAFT_SAVE_TEST_FILE_PATH = os.path.abspath("{0}/../samples/example.savetest.sddraft".format(os.path.dirname(__file__)))
SDDRAFT_FILE_PATH_COPY = os.path.abspath("{0}/../samples/example.copy.sddraft".format(os.path.dirname(__file__)))

"""Not implemented in agsconfig
@pytest.fixture
def server_ext():
    shutil.copyfile(SDDRAFT_FILE_PATH, SDDRAFT_FILE_PATH_COPY)
    return SchematicsServerExtension(SDDraftEditor(SDDRAFT_FILE_PATH_COPY))

@pytest.mark.parametrize(("capabilities", "expected", "ex"), [
    (["Query"], [SchematicsServerExtension.Capability.query], None),
    (["quErY"], None, ValueError),
    ([SchematicsServerExtension.Capability.query, SchematicsServerExtension.Capability.editing], [SchematicsServerExtension.Capability.query, SchematicsServerExtension.Capability.editing], None),
    (["Foo", "Bar"], None, ValueError),
    (["Query", 1], None, TypeError)
])
def test_capabilities(server_ext, capabilities, expected, ex):
    assert isinstance(type(server_ext).capabilities, property) == True
    if (ex != None):
        with pytest.raises(ex):
            server_ext.capabilities = capabilities
    else:
        server_ext.capabilities = capabilities
        assert set(server_ext.capabilities) == set(expected)

@pytest.mark.parametrize(("enabled", "expected"), TRUEISH_TEST_PARAMS)
def test_enabled(server_ext, enabled, expected):
    server_ext.enabled = enabled
    assert server_ext.enabled == expected
"""