import os.path
import shutil

import arcpyext
import pytest

from arcpyext.publishing._wps_server_extension import WpsServerExtension
from arcpyext.publishing._sddraft_editor import SDDraftEditor
from .. helpers import *

SDDRAFT_FILE_PATH = os.path.abspath("{0}/../samples/pythongpservice.sddraft".format(os.path.dirname(__file__)))
SDDRAFT_FILE_PATH_COPY = os.path.abspath("{0}/../samples/pythongpservice.copy.sddraft".format(os.path.dirname(__file__)))
SDDRAFT_SAVE_TEST_FILE_PATH = os.path.abspath("{0}/../samples/pythongpservice.savetest.sddraft".format(os.path.dirname(__file__)))

@pytest.fixture
def server_ext():
    shutil.copyfile(SDDRAFT_FILE_PATH, SDDRAFT_FILE_PATH_COPY)
    return WpsServerExtension(SDDraftEditor(SDDRAFT_FILE_PATH_COPY))

from arcpyext.publishing._ogc_metadata_extension_mixin import *
from arcpyext.publishing._custom_get_capabilities_extension_mixin import *

@pytest.mark.parametrize(("app_schema_prefix"), [
    ("my_service")
])
def test_app_schema_prefix(server_ext, app_schema_prefix):
    assert isinstance(type(server_ext).app_schema_prefix, property) == True
    server_ext.app_schema_prefix = app_schema_prefix
    assert server_ext.app_schema_prefix == app_schema_prefix

def test_capabilities(server_ext):
    assert isinstance(type(server_ext).capabilities, property) == True
    assert server_ext.capabilities == None
    with pytest.raises(NotImplementedError):
        server_ext.capabilities = "Blah"

@pytest.mark.parametrize(("contact_instructions"), [
    ("Contact Doe between 8am and 6pm Central Time for support.")
])
def test_contact_instructions(server_ext, contact_instructions):
    assert isinstance(type(server_ext).contact_instructions, property) == True
    server_ext.contact_instructions = contact_instructions
    assert server_ext.contact_instructions == contact_instructions

@pytest.mark.parametrize(("hours_of_service"), [
    ("24/7")
])
def test_hours_of_service(server_ext, hours_of_service):
    assert isinstance(type(server_ext).hours_of_service, property) == True
    server_ext.hours_of_service = hours_of_service
    assert server_ext.hours_of_service == hours_of_service

@pytest.mark.parametrize(("site"), [
    ("http://www.foobar.com/")
])
def test_provider_site(server_ext, site):
    assert isinstance(type(server_ext).provider_site, property) == True
    server_ext.provider_site = site
    assert server_ext.provider_site == site

@pytest.mark.parametrize(("service_type"), [
    ("WFS")
])
def test_service_type(server_ext, service_type):
    assert isinstance(type(server_ext).service_type, property) == True
    server_ext.service_type = service_type
    assert server_ext.service_type == service_type

@pytest.mark.parametrize(("service_type_version"), [
    ("1.0.0"),
    ("1.1.0"),
])
def test_service_type_version(server_ext, service_type_version):
    assert isinstance(type(server_ext).service_type_version, property) == True
    server_ext.service_type_version = service_type_version
    assert server_ext.service_type_version == service_type_version