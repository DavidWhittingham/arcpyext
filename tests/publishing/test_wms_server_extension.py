import os.path
import shutil

import arcpyext
import pytest

from arcpyext.publishing._wms_server_extension import WmsServerExtension
from arcpyext.publishing._sddraft_editor import SDDraftEditor
from .. helpers import *

SDDRAFT_FILE_PATH = os.path.abspath("{0}/../samples/example.sddraft".format(os.path.dirname(__file__)))
SDDRAFT_FILE_PATH_COPY = os.path.abspath("{0}/../samples/example.copy.sddraft".format(os.path.dirname(__file__)))
SDDRAFT_SAVE_TEST_FILE_PATH = os.path.abspath("{0}/../samples/example.savetest.sddraft".format(os.path.dirname(__file__)))

@pytest.fixture
def server_ext():
    shutil.copyfile(SDDRAFT_FILE_PATH, SDDRAFT_FILE_PATH_COPY)
    return WmsServerExtension(SDDraftEditor(SDDRAFT_FILE_PATH_COPY))

from ogc_metadata_extension_mixin import *
from custom_get_capabilities_extension_mixin import *

@pytest.mark.parametrize(("srs", "expected"), [
    (["EPSG:102100","EPSG:102113","EPSG:3857"], ["EPSG:102100","EPSG:102113","EPSG:3857"]),
    ("EPSG:102100,EPSG:102113,EPSG:3857", ["EPSG:102100","EPSG:102113","EPSG:3857"]),
    (None, []),
    ("", [])
])
def test_additional_spatial_ref_sys(server_ext, srs, expected):
    server_ext.additional_spatial_ref_sys = srs
    assert set(server_ext.additional_spatial_ref_sys) == set(expected)

@pytest.mark.parametrize(("address_type"), [
    ("postal")
])
def test_address_type(server_ext, address_type):
    server_ext.address_type = address_type
    assert server_ext.address_type == address_type

@pytest.mark.parametrize(("capabilities", "expected", "ex"), [
    (["GetCapabilities"], [WmsServerExtension.Capability.get_capabilities], None),
    (["GetFeatureInfo", "GetMap"], [WmsServerExtension.Capability.get_feature_info, WmsServerExtension.Capability.get_map], None),
    (["getfeatureinfo"], None, ValueError),
    ([WmsServerExtension.Capability.get_styles], [WmsServerExtension.Capability.get_styles], None),
    (["FooBar"], None, ValueError),
    ([1], None, TypeError)
])
def test_capabilities(server_ext, capabilities, expected, ex):
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

@pytest.mark.parametrize(("fees"), [
    ("none.")
])
def test_fees(server_ext, fees):
    server_ext.fees = fees
    assert server_ext.fees == fees

@pytest.mark.parametrize(("enabled", "expected"), TRUEISH_TEST_PARAMS)
def test_inherit_layer_names(server_ext, enabled, expected):
    server_ext.inherit_layer_names = enabled
    assert server_ext.inherit_layer_names == expected

@pytest.mark.parametrize(("keyword"), [
    ("Test Keywords")
])
def test_keyword(server_ext, keyword):
    server_ext.keyword = keyword
    assert server_ext.keyword == keyword

@pytest.mark.parametrize(("name", "ex"), [
    ("TestName", None),
    ("", ValueError),
    (None, ValueError),
    ("\r\n\t", ValueError)
])
def test_name(server_ext, name, ex):
    if (ex != None):
        with pytest.raises(ex):
            server_ext.name = name
    else:
        server_ext.name = name
        assert server_ext.name == name

@pytest.mark.parametrize(("custom_path"), [
    ("http://www.myserver.com/ArcGIS/WMS/services/MyStyles.xml")
])
def test_path_to_custom_sld_file(server_ext, custom_path):
    server_ext.path_to_custom_sld_file = custom_path
    assert server_ext.path_to_custom_sld_file == custom_path

@pytest.mark.parametrize(("post_code", "expected", "ex"), [
    ("10", 10, None),
    (10245, 10245, None),
    (0, None, ValueError),
    (-45, None, ValueError)
])
def test_post_code(server_ext, post_code, expected, ex):
    if (ex != None):
        with pytest.raises(ex):
            server_ext.post_code = post_code
    else:
        server_ext.post_code = post_code
        assert server_ext.post_code == expected

@pytest.mark.parametrize(("enabled", "expected"), TRUEISH_TEST_PARAMS)
def test_reaspect(server_ext, enabled, expected):
    server_ext.reaspect = enabled
    assert server_ext.reaspect == expected

@pytest.mark.parametrize(("title"), [
    ("This is a test map title.")
])
def test_title(server_ext, title):
    server_ext.title = title
    assert server_ext.title == title