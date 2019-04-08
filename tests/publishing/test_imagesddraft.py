from __future__ import (absolute_import, division, print_function, unicode_literals)
from builtins import (bytes, dict, int, list, object, range, str, ascii, chr, hex, input, next, oct, open, pow, round,
                      super, filter, map, zip)

import os.path
import shutil

import arcpyext
import agsconfig
import pytest

from .. helpers import *

SDDRAFT_FILE_PATH = os.path.abspath("{0}/../samples/imageservice.sddraft".format(os.path.dirname(__file__)))
SDDRAFT_FILE_PATH_COPY = os.path.abspath("{0}/../samples/imageservice.copy.sddraft".format(os.path.dirname(__file__)))
SDDRAFT_SAVE_TEST_FILE_PATH = os.path.abspath("{0}/../samples/imageservice.savetest.sddraft".format(os.path.dirname(__file__)))

@pytest.fixture
def sddraft():
    shutil.copyfile(SDDRAFT_FILE_PATH, SDDRAFT_FILE_PATH_COPY)
    with open(SDDRAFT_FILE_PATH_COPY, "rb+") as file:
        return agsconfig.load_image_sddraft(file)

@pytest.mark.parametrize(("methods", "expected", "ex"), [
    ([agsconfig.ImageServer.CompressionMethod.none], [agsconfig.ImageServer.CompressionMethod.none], None),
    (
        [agsconfig.ImageServer.CompressionMethod.jpeg, agsconfig.ImageServer.CompressionMethod.lz77],
        [agsconfig.ImageServer.CompressionMethod.jpeg, agsconfig.ImageServer.CompressionMethod.lz77],
        None
    ),
    (["LERC"], [agsconfig.ImageServer.CompressionMethod.lerc], None),
    (["Fail"], None, ValueError),
    ([123], None, ValueError)
])
def test_allowed_compression_methods(sddraft, methods, expected, ex):
    if ex != None:
        with pytest.raises(ex):
            sddraft.allowed_compressions = methods
    else:
        sddraft.allowed_compressions = methods
        assert sddraft.allowed_compressions == expected

@pytest.mark.parametrize(("methods", "expected", "ex"), [
    ([agsconfig.ImageServer.MosaicMethod.north_west], [agsconfig.ImageServer.MosaicMethod.north_west], None),
    (
        [agsconfig.ImageServer.MosaicMethod.lock_raster, agsconfig.ImageServer.MosaicMethod.center],
        [agsconfig.ImageServer.MosaicMethod.lock_raster, agsconfig.ImageServer.MosaicMethod.center],
        None
    ),
    (["Nadir", "Viewpoint"], [agsconfig.ImageServer.MosaicMethod.nadir, agsconfig.ImageServer.MosaicMethod.viewpoint], None),
    (["Blah"], None, ValueError)
])
def test_allowed_mosaic_methods(sddraft, methods, expected, ex):
    if ex != None:
        with pytest.raises(ex):
            sddraft.allowed_mosaic_methods = methods
    else:
        sddraft.allowed_mosaic_methods = methods
        assert set(sddraft.allowed_mosaic_methods) == set(expected)

@pytest.mark.parametrize(("fields"), [
    (["A", "B", "C"]),
    (("D", "E", "F"))
])
def test_available_fields(sddraft, fields):
    sddraft.available_fields = fields
    assert set(sddraft.available_fields) == set(fields)

@pytest.mark.parametrize(("capabilities", "expected", "ex"), [
    ([agsconfig.ImageServer.Capability.catalog], [agsconfig.ImageServer.Capability.catalog], None),
    ([], [], None),
    (["Edit"], [agsconfig.ImageServer.Capability.edit], None),
    (["Fail"], None, ValueError),
    ([123], None, ValueError)
])
def test_capabilities(sddraft, capabilities, expected, ex):
    if ex != None:
        with pytest.raises(ex):
            sddraft.capabilities = capabilities
    else:
        sddraft.capabilities = capabilities
        assert set(sddraft.capabilities) == set(expected)

@pytest.mark.parametrize(("method", "ex"), [
    (agsconfig.ImageServer.ResamplingMethod.nearest_neighbor, None),
    (agsconfig.ImageServer.ResamplingMethod.bilinear, None),
    (agsconfig.ImageServer.ResamplingMethod.cubic, None),
    (agsconfig.ImageServer.ResamplingMethod.majority, None),
    (99, ValueError)
])
def test_default_resampling_method(sddraft, method, ex):
    if ex != None:
        with pytest.raises(ex):
            sddraft.default_resampling_method = method
    else:
        sddraft.default_resampling_method = method
        assert sddraft.default_resampling_method == method

@pytest.mark.parametrize(("count", "ex"), [
    (50, None),
    (None, None),
    (0, None),
    (-1, ValueError)
])
def test_max_download_image_count(sddraft, count, ex):
    if (ex != None):
        with pytest.raises(ex):
            sddraft.max_download_image_count = count
    else:
        sddraft.max_download_image_count = count
        assert sddraft.max_download_image_count == count

@pytest.mark.parametrize(("limit", "ex"), [
    (50, None),
    (None, None),
    (0, None),
    (-1, ValueError)
])
def test_max_download_size_limit(sddraft, limit, ex):
    if (ex != None):
        with pytest.raises(ex):
            sddraft.max_download_size_limit = limit
    else:
        sddraft.max_download_size_limit = limit
        assert sddraft.max_download_size_limit == limit

@pytest.mark.parametrize(("count", "ex"), [
    (30, None),
    (None, None),
    (-1, ValueError)
])
def test_max_mosaic_image_count(sddraft, count, ex):
    if (ex != None):
        with pytest.raises(ex):
            sddraft.max_mosaic_image_count = count
    else:
        sddraft.max_mosaic_image_count = count
        assert sddraft.max_mosaic_image_count == count

@pytest.mark.parametrize(("enabled", "expected"), TRUEISH_TEST_PARAMS)
def test_return_jpgpng_as_jpg(sddraft, enabled, expected):
    sddraft.return_jpgpng_as_jpg = enabled
    assert sddraft.return_jpgpng_as_jpg == expected

@pytest.mark.parametrize(("prop_dict"), [
    ({
        "allowed_compressions": [
            "None",
            "JPEG",
            "LZ77",
            "LERC"
        ],
        "allowed_mosaic_methods": [
            "NorthWest",
            "Center",
            "LockRaster",
            "ByAttribute",
            "Nadir",
            "Viewpoint",
            "Seamline",
            "None"
        ],
        "available_fields": ["Field1", "Field2", "Field3"],
        "capabilities": [
            "Catalog",
            "Edit",
            "Mensuration",
            "Pixels",
            "Download",
            "Image",
            "Metadata"
        ],
        "cluster": "clusterNameHere",
        "default_resampling_method": 1,
        "description": "Service description goes here.",
        "folder": "Imagery",
        "high_isolation": True,
        "idle_timeout": 600,
        "instances_per_container": 4,
        "jpip_server": {
            "enabled": True
        },
        "keep_cache": True,
        "max_download_image_count": 100,
        "max_download_size_limit": 100,
        "max_image_height": 1024,
        "max_image_width": 1024,
        "max_instances": 4,
        "max_mosaic_image_count": 20,
        "max_record_count": 1000,
        "min_instances": 1,
        "name": "ServiceNameGoesHere",
        "recycle_interval": 24,
        "recycle_start_time": "23:00",
        "replace_existing": True,
        "return_jpgpng_as_jpg": True,
        "summary": "Map service summary goes here.",
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
        }
    })
])
def test_set_props_from_dict(sddraft, prop_dict):
    sddraft._set_props_from_dict(prop_dict)
    assert set([c.value for c in sddraft.allowed_compressions]) == set(prop_dict["allowed_compressions"])
    assert set([c.value for c in sddraft.allowed_mosaic_methods]) == set(prop_dict["allowed_mosaic_methods"])
    assert set(sddraft.available_fields) == set(prop_dict["available_fields"])
    assert set([c.value for c in sddraft.capabilities]) == set(prop_dict["capabilities"])
    assert sddraft.cluster == prop_dict["cluster"]
    assert sddraft.default_resampling_method.value == prop_dict["default_resampling_method"]
    assert sddraft.description == prop_dict["description"]
    assert sddraft.folder == prop_dict["folder"]
    assert sddraft.high_isolation == prop_dict["high_isolation"]
    assert sddraft.idle_timeout == prop_dict["idle_timeout"]
    assert sddraft.instances_per_container == prop_dict["instances_per_container"]
    assert sddraft.keep_cache == prop_dict["keep_cache"]
    assert sddraft.max_download_image_count == prop_dict["max_download_image_count"]
    assert sddraft.max_download_size_limit == prop_dict["max_download_size_limit"]
    assert sddraft.max_image_height == prop_dict["max_image_height"]
    assert sddraft.max_image_width == prop_dict["max_image_width"]
    assert sddraft.max_instances == prop_dict["max_instances"]
    assert sddraft.max_mosaic_image_count == prop_dict["max_mosaic_image_count"]
    #assert sddraft.max_record_count == prop_dict["max_record_count"]
    assert sddraft.min_instances == prop_dict["min_instances"]
    assert sddraft.name == prop_dict["name"]
    assert sddraft.recycle_interval == prop_dict["recycle_interval"]
    assert "{0:02d}:{1:02d}".format(sddraft.recycle_start_time.hour, sddraft.recycle_start_time.minute) == prop_dict["recycle_start_time"]
    assert sddraft.replace_existing == prop_dict["replace_existing"]
    assert sddraft.return_jpgpng_as_jpg == prop_dict["return_jpgpng_as_jpg"]
    assert sddraft.summary == prop_dict["summary"]
    assert sddraft.usage_timeout == prop_dict["usage_timeout"]
    assert sddraft.wait_timeout == prop_dict["wait_timeout"]

    # JPIP Server
    assert sddraft.jpip_server.enabled == prop_dict["jpip_server"]["enabled"]

    # WCS Server
    assert sddraft.wcs_server.abstract == prop_dict["wcs_server"]["abstract"]
    assert sddraft.wcs_server.access_constraints == prop_dict["wcs_server"]["access_constraints"]
    assert sddraft.wcs_server.address == prop_dict["wcs_server"]["address"]
    #assert sddraft.wcs_server.administrative_area == prop_dict["wcs_server"]["administrative_area"]
    assert sddraft.wcs_server.city == prop_dict["wcs_server"]["city"]
    assert sddraft.wcs_server.country == prop_dict["wcs_server"]["country"]
    assert sddraft.wcs_server.custom_get_capabilities == prop_dict["wcs_server"]["custom_get_capabilities"]
    #assert sddraft.wcs_server.email == prop_dict["wcs_server"]["email"]
    assert sddraft.wcs_server.enabled == prop_dict["wcs_server"]["enabled"]
    #assert sddraft.wcs_server.facsimile == prop_dict["wcs_server"]["facsimile"]
    assert sddraft.wcs_server.fees == prop_dict["wcs_server"]["fees"]
    #assert sddraft.wcs_server.individual_name == prop_dict["wcs_server"]["individual_name"]
    assert sddraft.wcs_server.keyword == prop_dict["wcs_server"]["keyword"]
    assert sddraft.wcs_server.name == prop_dict["wcs_server"]["name"]
    #assert sddraft.wcs_server.organization == prop_dict["wcs_server"]["organization"]
    assert sddraft.wcs_server.path_to_custom_get_capabilities_files == prop_dict["wcs_server"]["path_to_custom_get_capabilities_files"]
    #assert sddraft.wcs_server.phone == prop_dict["wcs_server"]["phone"]
    #assert sddraft.wcs_server.position_name == prop_dict["wcs_server"]["position_name"]
    #assert sddraft.wcs_server.post_code == prop_dict["wcs_server"]["post_code"]
    assert sddraft.wcs_server.title == prop_dict["wcs_server"]["title"]

    # WMS Server
    assert sddraft.wms_server.abstract == prop_dict["wms_server"]["abstract"]
    assert sddraft.wms_server.access_constraints == prop_dict["wms_server"]["access_constraints"]
    assert sddraft.wms_server.address == prop_dict["wms_server"]["address"]
    #assert sddraft.wms_server.administrative_area == prop_dict["wms_server"]["administrative_area"]
    assert sddraft.wms_server.address_type == prop_dict["wms_server"]["address_type"]
    assert set([c.value for c in sddraft.wms_server.capabilities]) == set(prop_dict["wms_server"]["capabilities"])
    assert sddraft.wms_server.city == prop_dict["wms_server"]["city"]
    assert sddraft.wms_server.country == prop_dict["wms_server"]["country"]
    assert sddraft.wms_server.custom_get_capabilities == prop_dict["wms_server"]["custom_get_capabilities"]
    #assert sddraft.wms_server.email == prop_dict["wms_server"]["email"]
    assert sddraft.wms_server.enabled == prop_dict["wms_server"]["enabled"]
    #assert sddraft.wms_server.facsimile == prop_dict["wms_server"]["facsimile"]
    assert sddraft.wms_server.fees == prop_dict["wms_server"]["fees"]
    assert sddraft.wms_server.inherit_layer_names == prop_dict["wms_server"]["inherit_layer_names"]
    #assert sddraft.wms_server.individual_name == prop_dict["wms_server"]["individual_name"]
    assert sddraft.wms_server.keyword == prop_dict["wms_server"]["keyword"]
    assert sddraft.wms_server.name == prop_dict["wms_server"]["name"]
    #assert sddraft.wms_server.organization == prop_dict["wms_server"]["organization"]
    assert sddraft.wms_server.path_to_custom_get_capabilities_files == prop_dict["wms_server"]["path_to_custom_get_capabilities_files"]
    assert sddraft.wms_server.path_to_custom_sld_file == prop_dict["wms_server"]["path_to_custom_sld_file"]
    #assert sddraft.wms_server.phone == prop_dict["wms_server"]["phone"]
    #assert sddraft.wms_server.position_name == prop_dict["wms_server"]["position_name"]
    assert sddraft.wms_server.post_code == prop_dict["wms_server"]["post_code"]
    assert sddraft.wms_server.title == prop_dict["wms_server"]["title"]
