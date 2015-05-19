import os.path
import shutil

import arcpyext
import pytest

from arcpyext.publishing import MapSDDraft
from arcpyext.publishing import SDDraftEditor
from .. helpers import *

SDDRAFT_FILE_PATH = os.path.abspath("{0}/../samples/example.sddraft".format(os.path.dirname(__file__)))
SDDRAFT_FILE_PATH_COPY = os.path.abspath("{0}/../samples/example.copy.sddraft".format(os.path.dirname(__file__)))
SDDRAFT_SAVE_TEST_FILE_PATH = os.path.abspath("{0}/../samples/example.savetest.sddraft".format(os.path.dirname(__file__)))

@pytest.fixture
def sddraft():
    shutil.copyfile(SDDRAFT_FILE_PATH, SDDRAFT_FILE_PATH_COPY)
    return MapSDDraft(SDDraftEditor(SDDRAFT_FILE_PATH_COPY))

from sddraftbase import *
from sddraft_cacheable import *

@pytest.mark.parametrize(("mode", "expected", "ex"), [
    (MapSDDraft.AntiAliasingMode.none, MapSDDraft.AntiAliasingMode.none, None),
    (MapSDDraft.AntiAliasingMode.fastest, MapSDDraft.AntiAliasingMode.fastest, None),
    (MapSDDraft.AntiAliasingMode.fast, MapSDDraft.AntiAliasingMode.fast, None),
    (MapSDDraft.AntiAliasingMode.normal, MapSDDraft.AntiAliasingMode.normal, None),
    (MapSDDraft.AntiAliasingMode.best, MapSDDraft.AntiAliasingMode.best, None),
    ("None", MapSDDraft.AntiAliasingMode.none, None),
    ("Fail", None, ValueError)
])
def test_aa_mode(sddraft, mode, expected, ex):
    if (ex != None):
        with pytest.raises(ex):
            sddraft.anti_aliasing_mode = mode
    else:
        sddraft.anti_aliasing_mode = mode
        assert sddraft.anti_aliasing_mode == expected

@pytest.mark.parametrize(("capabilities", "expected", "ex"), [
    ([MapSDDraft.Capability.map], [MapSDDraft.Capability.map], None),
    ([], [], None),
    (["Query"], [MapSDDraft.Capability.query], None),
    (["Fail"], None, ValueError),
    ([123], None, TypeError)
])
def test_capabilities(sddraft, capabilities, expected, ex):
    assert isinstance(type(sddraft).capabilities, property) == True
    if ex != None:
        with pytest.raises(ex):
            sddraft.capabilities = capabilities
    else:
        sddraft.capabilities = capabilities
        assert set(sddraft.capabilities) == set(expected)

@pytest.mark.parametrize(("disabled", "expected"), TRUEISH_TEST_PARAMS)
def test_disable_indentify_relates(sddraft, disabled, expected):
    sddraft.disable_identify_relates = disabled
    assert sddraft.disable_identify_relates == expected

@pytest.mark.parametrize(("enabled", "expected"), TRUEISH_TEST_PARAMS)
def test_enable_dynamic_layers(sddraft, enabled, expected):
    sddraft.enable_dynamic_layers = enabled
    assert sddraft.enable_dynamic_layers == expected

@pytest.mark.parametrize(("file_path", "equal"), [
    (SDDRAFT_FILE_PATH_COPY, True),
    ("./FooBar", False),
])
def test_file_path(sddraft, file_path, equal):
    assert (os.path.normpath(sddraft.file_path) == os.path.normpath(file_path)) == equal

@pytest.mark.parametrize(("name", "ex"), [
    ("TestName", None),
    ("", ValueError)
])
def test_name(sddraft, name, ex):
    if ex != None:
        with pytest.raises(ex):
            sddraft.name = name
    else:
        sddraft.name = name
        assert sddraft.name == name
        assert sddraft.wfs_server.name == name
        assert sddraft.wcs_server.name == name

@pytest.mark.parametrize(("prop_dict"), [
    ({
        "anti_aliasing_mode": "Fast",
        "capabilities": [
            "Map",
            "Query",
            "Data"
        ],
        "cluster": "clusterNameHere",
        "description": "Service description goes here.",
        "disable_identify_relates": True,
        "enable_dynamic_layers": True,
        "feature_server": {
            "allow_geometry_updates": True,
            "allow_others_to_delete": True,
            "allow_others_to_query": True,
            "allow_others_to_update": True,
            "allow_true_curves_updates": True,
            "capabilities": [
                "Create",
                "Query",
                "Update",
                "Delete",
                "Sync"
            ],
            "enable_ownership_based_access_control": True,
            "enable_z_defaults": True,
            "enabled": True,
            "max_record_count": 1000,
            "realm": "MyRealm",
            "z_default_value": 0.0
        },
        "folder": "ExampleServices",
        "high_isolation": True,
        "idle_timeout": 600,
        "instances_per_container": 4,
        "keep_cache": True,
        "kml_server": {
            "capabilities": [
                "SingleImage",
                "SeparateImages",
                "Vectors"
            ],
            "compatibility_mode": "GoogleEarth",
            "dpi": 96,
            "enabled": True,
            "feature_limit": 1000,
            "image_size": 2000,
            "link_name": "FooBarService",
            "link_description": "This is a service description.",
            "message": "This is the one-time message that appears on adding the service to a client.",
            "min_refresh_period": 30,
            "use_default_snippets": True,
            "use_network_link_control_tag": True
        },
        "max_instances": 4,
        "max_record_count": 1000,
        "min_instances": 1,
        "mobile_server": {
            "enabled": True
        },
        "na_server": {
            "enabled": True
        },
        "name": "ServiceNameGoesHere",
        "recycle_interval": 24,
        "recycle_start_time": "23:00",
        "replace_existing": True,
        "schema_locking_enabled": True,
        "schematics_server": {
            "capabilities": [
                "Query",
                "Editing"
            ],
            "enabled": True
        },
        "summary": "Map service summary goes here.",
        "text_anti_aliasing_mode": "Normal",
        "usage_timeout": 60,
        "wait_timeout": 600,
        "wcs_server": {
            "abstract": "This is an example abstract.",
            "access_constraints": "This service contains sensitive business data, INTERNAL USE ONLY.",
            "administrative_area": "State of FooBar",
            "address": "123 Fake St.",
            "city": "Faketown",
            "country": "Kingdom of FooBar",
            "custom_get_capabilities": True,
            "email": "email@example.com",
            "enabled": True,
            "facsimile": "+111 1111 1111",
            "fees": "Service is free for non-commercial use.",
            "individual_name": "Doe",
            "keyword": "FooBar, Spatial",
            "name": "FooBarService",
            "organization": "Fake Corp.",
            "path_to_custom_get_capabilities_files": "http://foobar.com/services/Wms/FooBarRoads",
            "phone": "+222 2222 2222",
            "position_name": "WMS Services Contact Officer",
            "post_code": 10532,
            "title": "FooBar Roads Service"
        },
        "wms_server": {
            "abstract": "This is an example abstract.",
            "access_constraints": "This service contains sensitive business data, INTERNAL USE ONLY.",
            "administrative_area": "State of FooBar",
            "address": "123 Fake St.",
            "address_type": "postal",
            "capabilities": [
                "GetCapabilities",
                "GetMap",
                "GetFeatureInfo",
                "GetStyles",
                "GetLegendGraphic",
                "GetSchemaExtension"
            ],
            "city": "Faketown",
            "country": "Kingdom of FooBar",
            "custom_get_capabilities": True,
            "email": "email@example.com",
            "enabled": True,
            "facsimile": "+111 1111 1111",
            "fees": "Service is free for non-commercial use.",
            "inherit_layer_names": True,
            "individual_name": "Doe",
            "keyword": "FooBar, Spatial",
            "name": "FooBarService",
            "organization": "Fake Corp.",
            "path_to_custom_get_capabilities_files": "http://foobar.com/services/Wms/FooBarRoads",
            "path_to_custom_sld_file": "http://foobar.com/services/FooBarRoads.sld",
            "phone": "+222 2222 2222",
            "position_name": "WMS Services Contact Officer",
            "post_code": 10532,
            "title": "FooBar Roads Service"
        },
        "wfs_server": {
            "abstract": "This is an example abstract.",
            "access_constraints": "This service contains sensitive business data, INTERNAL USE ONLY.",
            "address": "123 Fake St.",
            "administrative_area": "State of FooBar",
            "app_schema_prefix": "FooBar",
            "axis_order_wfs_10": "LongLat",
            "axis_order_wfs_11": "LatLong",
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
            "name": "FooBarService",
            "organization": "Fake Corp.",
            "path_to_custom_get_capabilities_files": "http://foobar.com/services/Wfs/Roads",
            "phone": "+222 2222 2222",
            "position_name": "WMS Services Contact Officer",
            "post_code": 10532,
            "provider_site": "http://www.foobar.com/",
            "service_type": "WFS",
            "service_type_version": "1.1.0",
            "title": "FooBar Roads Service"
        }
    })
])
def test_set_props_from_dict(sddraft, prop_dict):
    sddraft._set_props_from_dict(prop_dict)
    assert sddraft.anti_aliasing_mode.value == prop_dict["anti_aliasing_mode"]
    assert set([c.value for c in sddraft.capabilities]) == set(prop_dict["capabilities"])
    assert sddraft.cluster == prop_dict["cluster"]
    assert sddraft.description == prop_dict["description"]
    assert sddraft.disable_identify_relates == prop_dict["disable_identify_relates"]
    assert sddraft.enable_dynamic_layers == prop_dict["enable_dynamic_layers"]
    assert sddraft.folder == prop_dict["folder"]
    assert sddraft.high_isolation == prop_dict["high_isolation"]
    assert sddraft.idle_timeout == prop_dict["idle_timeout"]
    assert sddraft.instances_per_container == prop_dict["instances_per_container"]
    assert sddraft.keep_cache == prop_dict["keep_cache"]
    assert sddraft.max_instances == prop_dict["max_instances"]
    assert sddraft.max_record_count == prop_dict["max_record_count"]
    assert sddraft.min_instances == prop_dict["min_instances"]
    assert sddraft.name == prop_dict["name"]
    assert sddraft.recycle_interval == prop_dict["recycle_interval"]
    assert "{0:02d}:{1:02d}".format(sddraft.recycle_start_time.hour, sddraft.recycle_start_time.minute) == prop_dict["recycle_start_time"]
    assert sddraft.replace_existing == prop_dict["replace_existing"]
    assert sddraft.schema_locking_enabled == prop_dict["schema_locking_enabled"]
    assert sddraft.summary == prop_dict["summary"]
    assert sddraft.text_anti_aliasing_mode.value == prop_dict["text_anti_aliasing_mode"]
    assert sddraft.usage_timeout == prop_dict["usage_timeout"]
    assert sddraft.wait_timeout == prop_dict["wait_timeout"]

    # Feature Server
    assert sddraft.feature_server.enabled == prop_dict["feature_server"]["enabled"]
    assert set([c.value for c in sddraft.feature_server.capabilities]) == set(prop_dict["feature_server"]["capabilities"])
    assert sddraft.feature_server.allow_geometry_updates == prop_dict["feature_server"]["allow_geometry_updates"]
    assert sddraft.feature_server.allow_others_to_delete == prop_dict["feature_server"]["allow_others_to_delete"]
    assert sddraft.feature_server.allow_others_to_query == prop_dict["feature_server"]["allow_others_to_query"]
    assert sddraft.feature_server.allow_others_to_update == prop_dict["feature_server"]["allow_others_to_update"]
    assert sddraft.feature_server.allow_true_curves_updates == prop_dict["feature_server"]["allow_true_curves_updates"]
    assert sddraft.feature_server.enable_ownership_based_access_control == prop_dict["feature_server"]["enable_ownership_based_access_control"]
    assert sddraft.feature_server.enable_z_defaults == prop_dict["feature_server"]["enable_z_defaults"]
    assert sddraft.feature_server.max_record_count == prop_dict["feature_server"]["max_record_count"]
    assert sddraft.feature_server.realm == prop_dict["feature_server"]["realm"]
    assert sddraft.feature_server.z_default_value == prop_dict["feature_server"]["z_default_value"]

    # KML Server
    assert sddraft.kml_server.enabled == prop_dict["kml_server"]["enabled"]
    assert set([c.value for c in sddraft.kml_server.capabilities]) == set(prop_dict["kml_server"]["capabilities"])
    assert sddraft.kml_server.compatibility_mode.value == prop_dict["kml_server"]["compatibility_mode"]
    assert sddraft.kml_server.dpi == prop_dict["kml_server"]["dpi"]
    assert sddraft.kml_server.enabled == prop_dict["kml_server"]["enabled"]
    assert sddraft.kml_server.feature_limit == prop_dict["kml_server"]["feature_limit"]
    assert sddraft.kml_server.image_size == prop_dict["kml_server"]["image_size"]
    assert sddraft.kml_server.link_name == prop_dict["kml_server"]["link_name"]
    assert sddraft.kml_server.link_description == prop_dict["kml_server"]["link_description"]
    assert sddraft.kml_server.message == prop_dict["kml_server"]["message"]
    assert sddraft.kml_server.min_refresh_period == prop_dict["kml_server"]["min_refresh_period"]
    assert sddraft.kml_server.use_default_snippets == prop_dict["kml_server"]["use_default_snippets"]
    assert sddraft.kml_server.use_network_link_control_tag == prop_dict["kml_server"]["use_network_link_control_tag"]

    # Mobile Server
    assert sddraft.mobile_server.enabled == prop_dict["mobile_server"]["enabled"]

    # Network Analysis Server
    assert sddraft.na_server.enabled == prop_dict["na_server"]["enabled"]

    # Schematics Server
    assert sddraft.schematics_server.enabled == prop_dict["schematics_server"]["enabled"]
    assert set([c.value for c in sddraft.schematics_server.capabilities]) == set(prop_dict["schematics_server"]["capabilities"])

    # WCS Server
    assert sddraft.wcs_server.abstract == prop_dict["wcs_server"]["abstract"]
    assert sddraft.wcs_server.access_constraints == prop_dict["wcs_server"]["access_constraints"]
    assert sddraft.wcs_server.address == prop_dict["wcs_server"]["address"]
    assert sddraft.wcs_server.administrative_area == prop_dict["wcs_server"]["administrative_area"]
    assert sddraft.wcs_server.city == prop_dict["wcs_server"]["city"]
    assert sddraft.wcs_server.country == prop_dict["wcs_server"]["country"]
    assert sddraft.wcs_server.custom_get_capabilities == prop_dict["wcs_server"]["custom_get_capabilities"]
    assert sddraft.wcs_server.email == prop_dict["wcs_server"]["email"]
    assert sddraft.wcs_server.enabled == prop_dict["wcs_server"]["enabled"]
    assert sddraft.wcs_server.facsimile == prop_dict["wcs_server"]["facsimile"]
    assert sddraft.wcs_server.fees == prop_dict["wcs_server"]["fees"]
    assert sddraft.wcs_server.individual_name == prop_dict["wcs_server"]["individual_name"]
    assert sddraft.wcs_server.keyword == prop_dict["wcs_server"]["keyword"]
    assert sddraft.wcs_server.name == prop_dict["wcs_server"]["name"]
    assert sddraft.wcs_server.organization == prop_dict["wcs_server"]["organization"]
    assert sddraft.wcs_server.path_to_custom_get_capabilities_files == prop_dict["wcs_server"]["path_to_custom_get_capabilities_files"]
    assert sddraft.wcs_server.phone == prop_dict["wcs_server"]["phone"]
    assert sddraft.wcs_server.position_name == prop_dict["wcs_server"]["position_name"]
    assert sddraft.wcs_server.post_code == prop_dict["wcs_server"]["post_code"]
    assert sddraft.wcs_server.title == prop_dict["wcs_server"]["title"]

    # WMS Server
    assert sddraft.wms_server.abstract == prop_dict["wms_server"]["abstract"]
    assert sddraft.wms_server.access_constraints == prop_dict["wms_server"]["access_constraints"]
    assert sddraft.wms_server.address == prop_dict["wms_server"]["address"]
    assert sddraft.wms_server.administrative_area == prop_dict["wms_server"]["administrative_area"]
    assert sddraft.wms_server.address_type == prop_dict["wms_server"]["address_type"]
    assert set([c.value for c in sddraft.wms_server.capabilities]) == set(prop_dict["wms_server"]["capabilities"])
    assert sddraft.wms_server.city == prop_dict["wms_server"]["city"]
    assert sddraft.wms_server.country == prop_dict["wms_server"]["country"]
    assert sddraft.wms_server.custom_get_capabilities == prop_dict["wms_server"]["custom_get_capabilities"]
    assert sddraft.wms_server.email == prop_dict["wms_server"]["email"]
    assert sddraft.wms_server.enabled == prop_dict["wms_server"]["enabled"]
    assert sddraft.wms_server.facsimile == prop_dict["wms_server"]["facsimile"]
    assert sddraft.wms_server.fees == prop_dict["wms_server"]["fees"]
    assert sddraft.wms_server.inherit_layer_names == prop_dict["wms_server"]["inherit_layer_names"]
    assert sddraft.wms_server.individual_name == prop_dict["wms_server"]["individual_name"]
    assert sddraft.wms_server.keyword == prop_dict["wms_server"]["keyword"]
    assert sddraft.wms_server.name == prop_dict["wms_server"]["name"]
    assert sddraft.wms_server.organization == prop_dict["wms_server"]["organization"]
    assert sddraft.wms_server.path_to_custom_get_capabilities_files == prop_dict["wms_server"]["path_to_custom_get_capabilities_files"]
    assert sddraft.wms_server.path_to_custom_sld_file == prop_dict["wms_server"]["path_to_custom_sld_file"]
    assert sddraft.wms_server.phone == prop_dict["wms_server"]["phone"]
    assert sddraft.wms_server.position_name == prop_dict["wms_server"]["position_name"]
    assert sddraft.wms_server.post_code == prop_dict["wms_server"]["post_code"]
    assert sddraft.wms_server.title == prop_dict["wms_server"]["title"]

    # WFS Server
    assert sddraft.wfs_server.abstract == prop_dict["wfs_server"]["abstract"]
    assert sddraft.wfs_server.access_constraints == prop_dict["wfs_server"]["access_constraints"]
    assert sddraft.wfs_server.address == prop_dict["wfs_server"]["address"]
    assert sddraft.wfs_server.administrative_area == prop_dict["wfs_server"]["administrative_area"]
    assert sddraft.wfs_server.app_schema_prefix == prop_dict["wfs_server"]["app_schema_prefix"]
    assert sddraft.wfs_server.axis_order_wfs_10.value == prop_dict["wfs_server"]["axis_order_wfs_10"]
    assert sddraft.wfs_server.axis_order_wfs_11.value == prop_dict["wfs_server"]["axis_order_wfs_11"]
    assert sddraft.wfs_server.city == prop_dict["wfs_server"]["city"]
    assert sddraft.wfs_server.contact_instructions == prop_dict["wfs_server"]["contact_instructions"]
    assert sddraft.wfs_server.country == prop_dict["wfs_server"]["country"]
    assert sddraft.wfs_server.custom_get_capabilities == prop_dict["wfs_server"]["custom_get_capabilities"]
    assert sddraft.wfs_server.email == prop_dict["wfs_server"]["email"]
    assert sddraft.wfs_server.enable_transactions == prop_dict["wfs_server"]["enable_transactions"]
    assert sddraft.wfs_server.enabled == prop_dict["wfs_server"]["enabled"]
    assert sddraft.wfs_server.facsimile == prop_dict["wfs_server"]["facsimile"]
    assert sddraft.wfs_server.fees == prop_dict["wfs_server"]["fees"]
    assert sddraft.wfs_server.hours_of_service == prop_dict["wfs_server"]["hours_of_service"]
    assert sddraft.wfs_server.individual_name == prop_dict["wfs_server"]["individual_name"]
    assert sddraft.wfs_server.keyword == prop_dict["wfs_server"]["keyword"]
    assert sddraft.wfs_server.name == prop_dict["wfs_server"]["name"]
    assert sddraft.wfs_server.organization == prop_dict["wfs_server"]["organization"]
    assert sddraft.wfs_server.path_to_custom_get_capabilities_files == prop_dict["wfs_server"]["path_to_custom_get_capabilities_files"]
    assert sddraft.wfs_server.phone == prop_dict["wfs_server"]["phone"]
    assert sddraft.wfs_server.position_name == prop_dict["wfs_server"]["position_name"]
    assert sddraft.wfs_server.post_code == prop_dict["wfs_server"]["post_code"]
    assert sddraft.wfs_server.provider_site == prop_dict["wfs_server"]["provider_site"]
    assert sddraft.wfs_server.service_type == prop_dict["wfs_server"]["service_type"]
    assert sddraft.wfs_server.service_type_version == prop_dict["wfs_server"]["service_type_version"]
    assert sddraft.wfs_server.title == prop_dict["wfs_server"]["title"]


def test_save(sddraft):
    sddraft.save()
    assert True

@pytest.mark.parametrize(("output"), [
    (SDDRAFT_SAVE_TEST_FILE_PATH)
])
def test_save_a_copy(sddraft, output):
    sddraft.save_a_copy(output)
    assert os.path.isfile(output) == True

@pytest.mark.parametrize(("enabled", "expected"), TRUEISH_TEST_PARAMS)
def test_schema_locking_enabled(sddraft, enabled, expected):
    sddraft.schema_locking_enabled = enabled
    assert sddraft.schema_locking_enabled == expected

@pytest.mark.parametrize(("mode", "expected", "ex"), [
    (MapSDDraft.TextAntiAliasingMode.none, MapSDDraft.TextAntiAliasingMode.none, None),
    (MapSDDraft.TextAntiAliasingMode.force, MapSDDraft.TextAntiAliasingMode.force, None),
    (MapSDDraft.TextAntiAliasingMode.normal, MapSDDraft.TextAntiAliasingMode.normal, None),
    ("None", MapSDDraft.TextAntiAliasingMode.none, None),
    ("Fail", None, ValueError)
])
def test_text_aa_mode(sddraft, mode, expected, ex):
    if (ex != None):
        with pytest.raises(ex):
            sddraft.text_anti_aliasing_mode = mode
    else:
        sddraft.text_anti_aliasing_mode = mode
        assert sddraft.text_anti_aliasing_mode == expected