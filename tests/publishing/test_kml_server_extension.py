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
        return agsconfig.load_map_sddraft(file).kml_server

@pytest.mark.parametrize(("capabilities", "expected", "ex"), [
    (["SingleImage"], [agsconfig.KmlServerExtension.Capability.single_image], None),
    (["sEpaRateImageS"], None, ValueError),
    ([agsconfig.KmlServerExtension.Capability.separate_images, agsconfig.KmlServerExtension.Capability.vectors], [agsconfig.KmlServerExtension.Capability.separate_images, agsconfig.KmlServerExtension.Capability.vectors], None),
    (["Foo", "Bar"], None, ValueError),
    (["SingleImage", 1], None, ValueError)
])
def test_capabilities(server_ext, capabilities, expected, ex):
    if (ex != None):
        with pytest.raises(ex):
            server_ext.capabilities = capabilities
    else:
        server_ext.capabilities = capabilities
        assert set(server_ext.capabilities) == set(expected)

@pytest.mark.parametrize(("compatibility_mode", "expected", "ex"), [
    ("GoogleEarth", agsconfig.KmlServerExtension.CompatibilityMode.google_earth, None),
    ("gooGleEarTh", None, ValueError),
    (agsconfig.KmlServerExtension.CompatibilityMode.google_mobile, agsconfig.KmlServerExtension.CompatibilityMode.google_mobile, None),
    (agsconfig.KmlServerExtension.CompatibilityMode.google_maps, agsconfig.KmlServerExtension.CompatibilityMode.google_maps, None),
    ("Foo", None, ValueError),
    (1, None, ValueError)
])
def test_compatibility_mode(server_ext, compatibility_mode, expected, ex):
    if (ex != None):
        with pytest.raises(ex):
            server_ext.compatibility_mode = compatibility_mode
    else:
        server_ext.compatibility_mode = compatibility_mode
        assert server_ext.compatibility_mode == expected

@pytest.mark.parametrize(("dpi", "expected", "ex"), [
    ("96", 96, None),
    (120, 120, None),
    (0, 0, ValueError),
    (-100, None, ValueError),
    ("FooBar", None, ValueError)
])
def test_dpi(server_ext, dpi, expected, ex):
    if ex is not None:
        with pytest.raises(ex):
            server_ext.dpi = dpi
    else:
        server_ext.dpi = dpi
        assert server_ext.dpi == expected

@pytest.mark.parametrize(("feature_limit", "expected", "ex"), [
    ("1000", 1000, None),
    (20000, 20000, None),
    (-1000, None, ValueError),
    ("FooBar", None, ValueError)
])
def test_feature_limit(server_ext, feature_limit, expected, ex):
    if ex is not None:
        with pytest.raises(ex):
            server_ext.feature_limit = feature_limit
    else:
        server_ext.feature_limit = feature_limit
        assert server_ext.feature_limit == expected

@pytest.mark.parametrize(("image_size", "expected", "ex"), [
    ("1000", 1000, None),
    (20000, 20000, None),
    (0, 0, None),
    (-1000, None, ValueError),
    ("FooBar", None, ValueError)
])
def test_image_size(server_ext, image_size, expected, ex):
    if ex is not None:
        with pytest.raises(ex):
            server_ext.image_size = image_size
    else:
        server_ext.image_size = image_size
        assert server_ext.image_size == expected

@pytest.mark.parametrize(("link_name"), [
    ("test link name")
])
def test_link_name(server_ext, link_name):
    server_ext.link_name = link_name
    assert server_ext.link_name == link_name

@pytest.mark.parametrize(("link_description"), [
    ("test link description")
])
def test_link_description(server_ext, link_description):
    server_ext.link_description = link_description
    assert server_ext.link_description == link_description

@pytest.mark.parametrize(("message"), [
    ("test one time message")
])
def test_message(server_ext, message):
    server_ext.message = message
    assert server_ext.message == message

@pytest.mark.parametrize(("min_refresh_period", "expected", "ex"), [
    ("10", 10, None),
    (30, 30, None),
    (0, 0, None),
    (-1000, None, ValueError),
    ("FooBar", None, ValueError)
])
def test_min_refresh_period(server_ext, min_refresh_period, expected, ex):
    if ex is not None:
        with pytest.raises(ex):
            server_ext.min_refresh_period = min_refresh_period
    else:
        server_ext.min_refresh_period = min_refresh_period
        assert server_ext.min_refresh_period == expected

@pytest.mark.parametrize(("enabled", "expected"), TRUEISH_TEST_PARAMS)
def test_use_default_snippets(server_ext, enabled, expected):
    server_ext.use_default_snippets = enabled
    assert server_ext.use_default_snippets == expected

@pytest.mark.parametrize(("enabled", "expected"), TRUEISH_TEST_PARAMS)
def test_use_network_link_control_tag(server_ext, enabled, expected):
    server_ext.use_network_link_control_tag = enabled
    assert server_ext.use_network_link_control_tag == expected