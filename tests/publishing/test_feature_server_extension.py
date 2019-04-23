# Python 2/3 compatibility
# pylint: disable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position
from __future__ import (absolute_import, division, print_function, unicode_literals)
from future.builtins import *
from future.builtins.disabled import *
from future.standard_library import install_aliases
install_aliases()
# pylint: enable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position

import os.path
import shutil

import arcpyext
import agsconfig
import pytest

from .. helpers import *

SDDRAFT_FILE_PATH = os.path.abspath("{0}/../samples/example.sddraft".format(os.path.dirname(__file__)))
SDDRAFT_SAVE_TEST_FILE_PATH = os.path.abspath("{0}/../samples/example.savetest.sddraft".format(os.path.dirname(__file__)))
SDDRAFT_FILE_PATH_COPY = os.path.abspath("{0}/../samples/example.copy.sddraft".format(os.path.dirname(__file__)))

@pytest.fixture
def server_ext():
    shutil.copyfile(SDDRAFT_FILE_PATH, SDDRAFT_FILE_PATH_COPY)
    with open(SDDRAFT_FILE_PATH_COPY, "rb+") as file:
        return agsconfig.load_map_sddraft(file).feature_server

@pytest.mark.parametrize(("enabled", "expected"), TRUEISH_TEST_PARAMS)
def test_allow_geometry_updates(server_ext, enabled, expected):
    server_ext.allow_geometry_updates = enabled
    assert server_ext.allow_geometry_updates == expected

@pytest.mark.parametrize(("enabled", "expected"), TRUEISH_TEST_PARAMS)
def test_allow_others_to_delete(server_ext, enabled, expected):
    server_ext.allow_others_to_delete = enabled
    assert server_ext.allow_others_to_delete == expected

@pytest.mark.parametrize(("enabled", "expected"), TRUEISH_TEST_PARAMS)
def test_allow_others_to_query(server_ext, enabled, expected):
    server_ext.allow_others_to_query = enabled
    assert server_ext.allow_others_to_query == expected

@pytest.mark.parametrize(("enabled", "expected"), TRUEISH_TEST_PARAMS)
def test_allow_others_to_update(server_ext, enabled, expected):
    server_ext.allow_others_to_update = enabled
    assert server_ext.allow_others_to_update == expected

@pytest.mark.parametrize(("enabled", "expected"), TRUEISH_TEST_PARAMS)
def test_allow_true_curves_updates(server_ext, enabled, expected):
    server_ext.allow_true_curves_updates = enabled
    assert server_ext.allow_true_curves_updates == expected

@pytest.mark.parametrize(("capabilities", "expected", "ex"), [
    (["Query"], [agsconfig.FeatureServerExtension.Capability.query], None),
    (["quErY"], None, ValueError),
    ([agsconfig.FeatureServerExtension.Capability.create, agsconfig.FeatureServerExtension.Capability.update], [agsconfig.FeatureServerExtension.Capability.create, agsconfig.FeatureServerExtension.Capability.update], None),
    (["Foo", "Bar"], None, ValueError),
    (["Query", 1], None, ValueError)
])
def test_capabilities(server_ext, capabilities, expected, ex):
    if (ex != None):
        with pytest.raises(ex):
            server_ext.capabilities = capabilities
    else:
        server_ext.capabilities = capabilities
        assert set(server_ext.capabilities) == set(expected)

@pytest.mark.parametrize(("enabled", "expected"), TRUEISH_TEST_PARAMS)
def test_enable_ownership_based_access_control(server_ext, enabled, expected):
    server_ext.enable_ownership_based_access_control = enabled
    assert server_ext.enable_ownership_based_access_control == expected

@pytest.mark.parametrize(("enabled", "expected"), TRUEISH_TEST_PARAMS)
def test_enable_z_defaults(server_ext, enabled, expected):
    server_ext.enable_z_defaults = enabled
    assert server_ext.enable_z_defaults == expected

@pytest.mark.parametrize(("enabled", "expected"), TRUEISH_TEST_PARAMS)
def test_enabled(server_ext, enabled, expected):
    server_ext.enabled = enabled
    assert server_ext.enabled == expected

@pytest.mark.parametrize(("max_record_count", "expected", "ex"), [
    ("1000", 1000, None),
    (20000, 20000, None),
    (-1000, None, ValueError),
    ("FooBar", None, ValueError)
])
def test_max_record_count(server_ext, max_record_count, expected, ex):
    if ex != None:
        with pytest.raises(ex):
            server_ext.max_record_count = max_record_count
    else:
        server_ext.max_record_count = max_record_count
        assert server_ext.max_record_count == expected

@pytest.mark.parametrize(("realm"), [
    ("foobar")
])
def test_realm(server_ext, realm):
    server_ext.realm = realm
    assert server_ext.realm == realm

@pytest.mark.parametrize(("z_default_value", "expected", "ex"), [
    (0, 0, None),
    (0.0, 0, None),
    (98.1231212512512, 98.1231212512512, None),
    ("128.23423554", 128.23423554, None),
    ("FooBar", None, ValueError)
])
def test_z_default_value(server_ext, z_default_value, expected, ex):

    if ex != None:
        with pytest.raises(ex):
            server_ext.z_default_value = z_default_value
    else:
        server_ext.z_default_value = z_default_value
        assert server_ext.z_default_value == expected