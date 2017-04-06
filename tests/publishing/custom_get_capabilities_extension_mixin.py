import pytest
from .. helpers import *

@pytest.mark.parametrize(("enabled", "expected"), TRUEISH_TEST_PARAMS)
def test_custom_get_capabilities(server_ext, enabled, expected):
    server_ext.custom_get_capabilities = enabled
    assert server_ext.custom_get_capabilities == expected

@pytest.mark.parametrize(("custom_path"), [
    ("http://www.myserver.com/ArcGIS/WMS/services/Roads")
])
def test_path_to_custom_get_capabilities_files(server_ext, custom_path):
    server_ext.path_to_custom_get_capabilities_files = custom_path
    assert server_ext.path_to_custom_get_capabilities_files == custom_path