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
SDDRAFT_FILE_PATH_COPY = os.path.abspath("{0}/../samples/example.copy.sddraft".format(os.path.dirname(__file__)))
SDDRAFT_SAVE_TEST_FILE_PATH = os.path.abspath("{0}/../samples/example.savetest.sddraft".format(os.path.dirname(__file__)))

@pytest.fixture
def server_ext():
    shutil.copyfile(SDDRAFT_FILE_PATH, SDDRAFT_FILE_PATH_COPY)
    with open(SDDRAFT_FILE_PATH_COPY, "rb+") as file:
        return agsconfig.load_map_sddraft(file).wfs_server

@pytest.mark.parametrize(("app_schema_prefix"), [
    ("psl_test")
])
def test_app_schema_prefix(server_ext, app_schema_prefix):
    server_ext.app_schema_prefix = app_schema_prefix
    assert server_ext.app_schema_prefix == app_schema_prefix

@pytest.mark.parametrize(("axis_order", "expected", "ex"), [
    ("LatLong", agsconfig.WFSServerExtension.AxisOrder.lat_long, None),
    ("LongLat", agsconfig.WFSServerExtension.AxisOrder.long_lat, None),
    (agsconfig.WFSServerExtension.AxisOrder.lat_long, agsconfig.WFSServerExtension.AxisOrder.lat_long, None),
    ("FooBar", None, ValueError)
])
def test_axis_order_wfs_10(server_ext, axis_order, expected, ex):
    if ex != None:
        with pytest.raises(ex):
            server_ext.axis_order_wfs_10 = axis_order
    else:
        server_ext.axis_order_wfs_10 = axis_order
        assert server_ext.axis_order_wfs_10 == expected

@pytest.mark.parametrize(("axis_order", "expected", "ex"), [
    ("LatLong", agsconfig.WFSServerExtension.AxisOrder.lat_long, None),
    ("LongLat", agsconfig.WFSServerExtension.AxisOrder.long_lat, None),
    (agsconfig.WFSServerExtension.AxisOrder.lat_long, agsconfig.WFSServerExtension.AxisOrder.lat_long, None),
    ("FooBar", None, ValueError)
])
def test_axis_order_wfs_11(server_ext, axis_order, expected, ex):
    if ex != None:
        with pytest.raises(ex):
            server_ext.axis_order_wfs_11 = axis_order
    else:
        server_ext.axis_order_wfs_11 = axis_order
        assert server_ext.axis_order_wfs_11 == expected

def test_capabilities(server_ext):
    assert server_ext.capabilities == []
    with pytest.raises(ValueError):
        server_ext.capabilities = "Blah"

@pytest.mark.parametrize(("contact_instructions"), [
    ("Contact Doe between 8am and 6pm Central Time for support.")
])
def test_contact_instructions(server_ext, contact_instructions):
    server_ext.contact_instructions = contact_instructions
    assert server_ext.contact_instructions == contact_instructions

@pytest.mark.parametrize(("new_value", "expected"), TRUEISH_TEST_PARAMS)
def test_enable_transactions(server_ext, new_value, expected):
    server_ext.enable_transactions = new_value
    assert server_ext.enable_transactions == expected

@pytest.mark.parametrize(("hours_of_service"), [
    ("24/7")
])
def test_hours_of_service(server_ext, hours_of_service):
    server_ext.hours_of_service = hours_of_service
    assert server_ext.hours_of_service == hours_of_service

@pytest.mark.parametrize(("site"), [
    ("http://www.foobar.com/")
])
def test_provider_site(server_ext, site):
    server_ext.provider_site = site
    assert server_ext.provider_site == site

@pytest.mark.parametrize(("service_type"), [
    ("WFS")
])
def test_service_type(server_ext, service_type):
    server_ext.service_type = service_type
    assert server_ext.service_type == service_type

@pytest.mark.parametrize(("service_type_version"), [
    ("1.0.0"),
    ("1.1.0"),
])
def test_service_type_version(server_ext, service_type_version):
    server_ext.service_type_version = service_type_version
    assert server_ext.service_type_version == service_type_version