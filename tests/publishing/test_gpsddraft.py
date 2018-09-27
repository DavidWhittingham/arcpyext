from __future__ import (absolute_import, division, print_function, unicode_literals)
from builtins import (bytes, dict, int, list, object, range, str, ascii, chr, hex, input, next, oct, open, pow, round,
                      super, filter, map, zip)

import os.path
import shutil

import arcpyext
import pytest

from arcpyext.publishing._gpsddraft import GPSDDraft
from arcpyext.publishing._sddraft_editor import SDDraftEditor
from .. helpers import *

SDDRAFT_FILE_PATH = os.path.abspath("{0}/../samples/pythongpservice.sddraft".format(os.path.dirname(__file__)))
SDDRAFT_FILE_PATH_COPY = os.path.abspath("{0}/../samples/pythongpservice.copy.sddraft".format(os.path.dirname(__file__)))
SDDRAFT_SAVE_TEST_FILE_PATH = os.path.abspath("{0}/../samples/pythongpservice.savetest.sddraft".format(os.path.dirname(__file__)))

@pytest.fixture
def sddraft():
    shutil.copyfile(SDDRAFT_FILE_PATH, SDDRAFT_FILE_PATH_COPY)
    return GPSDDraft(SDDraftEditor(SDDRAFT_FILE_PATH_COPY))

from .sddraftbase import *
from .sddraft_max_record_count import *

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

@pytest.mark.parametrize(("prop_dict"), [
    ({
        "capabilities": ["Uploads"],
        "cluster": "clusterNameHere",
        "description": "Service description goes here.",
        "execution_type": "Asynchronous",
        "folder": "ExampleServices",
        "high_isolation": True,
        "idle_timeout": 600,
        "instances_per_container": 4,
        "max_instances": 4,
        "max_record_count": 1000,
        "min_instances": 1,
        "name": "ServiceNameGoesHere",
        "recycle_interval": 24,
        "recycle_start_time": "23:00",
        "replace_existing": True,
        "result_map_server": True,
        "summary": "Map service summary goes here.",
        "show_messages": "Error",
        "usage_timeout": 60,
        "wait_timeout": 600,
        "wps_server": {
            "abstract": "This is an example abstract.",
            "access_constraints": "This service contains sensitive business data, INTERNAL USE ONLY.",
            "address": "123 Fake St.",
            "administrative_area": "State of FooBar",
            "app_schema_prefix": "FooBar",
            "city": "Faketown",
            "contact_instructions": "Contact hours are 8am-6pm, UTC.",
            "country": "Kingdom of FooBar",
            "custom_get_capabilities": True,
            "email": "email@example.com",
            "enable_transactions": True,
            "enabled": True,
            "facsimile": "+111 1111 1111",
            "fees": "Service is free for non-commercial use.",
            "hours_of_service": "Service operates 24/7.",
            "individual_name": "Doe",
            "keyword": "FooBar, Spatial",
            "keywords_type": "Type Info",
            "name": "FooBarService",
            "organization": "Fake Corp.",
            "path_to_custom_get_capabilities_files": "http://foobar.com/services/Wfs/Roads",
            "phone": "+222 2222 2222",
            "position_name": "WMS Services Contact Officer",
            "post_code": 10532,
            "profile": "WPS profile",
            "provider_site": "http://www.foobar.com/",
            "role": "role info",
            "service_type": "WPS",
            "service_type_version": "1.1.0",
            "title": "FooBar Roads Service"
        }
    })
])
def test_set_props_from_dict(sddraft, prop_dict):
    sddraft._set_props_from_dict(prop_dict)
    assert set([c.value for c in sddraft.capabilities]) == set(prop_dict["capabilities"])
    assert sddraft.cluster == prop_dict["cluster"]
    assert sddraft.description == prop_dict["description"]
    assert sddraft.execution_type.value == prop_dict["execution_type"]
    assert sddraft.folder == prop_dict["folder"]
    assert sddraft.high_isolation == prop_dict["high_isolation"]
    assert sddraft.idle_timeout == prop_dict["idle_timeout"]
    assert sddraft.instances_per_container == prop_dict["instances_per_container"]
    assert sddraft.max_instances == prop_dict["max_instances"]
    assert sddraft.max_record_count == prop_dict["max_record_count"]
    assert sddraft.min_instances == prop_dict["min_instances"]
    assert sddraft.name == prop_dict["name"]
    assert sddraft.recycle_interval == prop_dict["recycle_interval"]
    assert "{0:02d}:{1:02d}".format(sddraft.recycle_start_time.hour, sddraft.recycle_start_time.minute) == prop_dict["recycle_start_time"]
    assert sddraft.replace_existing == prop_dict["replace_existing"]
    assert sddraft.summary == prop_dict["summary"]
    assert sddraft.show_messages.value == prop_dict["show_messages"]
    assert sddraft.usage_timeout == prop_dict["usage_timeout"]
    assert sddraft.wait_timeout == prop_dict["wait_timeout"]

    # WPS Server
    assert sddraft.wps_server.abstract == prop_dict["wps_server"]["abstract"]
    assert sddraft.wps_server.access_constraints == prop_dict["wps_server"]["access_constraints"]
    assert sddraft.wps_server.address == prop_dict["wps_server"]["address"]
    assert sddraft.wps_server.administrative_area == prop_dict["wps_server"]["administrative_area"]
    assert sddraft.wps_server.app_schema_prefix == prop_dict["wps_server"]["app_schema_prefix"]
    assert sddraft.wps_server.city == prop_dict["wps_server"]["city"]
    assert sddraft.wps_server.contact_instructions == prop_dict["wps_server"]["contact_instructions"]
    assert sddraft.wps_server.country == prop_dict["wps_server"]["country"]
    assert sddraft.wps_server.custom_get_capabilities == prop_dict["wps_server"]["custom_get_capabilities"]
    assert sddraft.wps_server.email == prop_dict["wps_server"]["email"]
    assert sddraft.wps_server.enabled == prop_dict["wps_server"]["enabled"]
    assert sddraft.wps_server.facsimile == prop_dict["wps_server"]["facsimile"]
    assert sddraft.wps_server.fees == prop_dict["wps_server"]["fees"]
    assert sddraft.wps_server.hours_of_service == prop_dict["wps_server"]["hours_of_service"]
    assert sddraft.wps_server.individual_name == prop_dict["wps_server"]["individual_name"]
    assert sddraft.wps_server.keyword == prop_dict["wps_server"]["keyword"]
    assert sddraft.wps_server.keywords_type == prop_dict["wps_server"]["keywords_type"]
    assert sddraft.wps_server.name == prop_dict["wps_server"]["name"]
    assert sddraft.wps_server.organization == prop_dict["wps_server"]["organization"]
    assert sddraft.wps_server.path_to_custom_get_capabilities_files == prop_dict["wps_server"]["path_to_custom_get_capabilities_files"]
    assert sddraft.wps_server.phone == prop_dict["wps_server"]["phone"]
    assert sddraft.wps_server.position_name == prop_dict["wps_server"]["position_name"]
    assert sddraft.wps_server.post_code == prop_dict["wps_server"]["post_code"]
    assert sddraft.wps_server.profile == prop_dict["wps_server"]["profile"]
    assert sddraft.wps_server.provider_site == prop_dict["wps_server"]["provider_site"]
    assert sddraft.wps_server.role == prop_dict["wps_server"]["role"]
    assert sddraft.wps_server.service_type == prop_dict["wps_server"]["service_type"]
    assert sddraft.wps_server.service_type_version == prop_dict["wps_server"]["service_type_version"]
    assert sddraft.wps_server.title == prop_dict["wps_server"]["title"]