# coding=utf-8
"""This module tests for the patches module."""

import os
import arcpyext
import pytest
from arcpy._mp import Map
from arcpyext._patches.patches import get_cim_version

MAP_A_PATH = os.path.abspath("{0}/../samples/test_mapping_complex.aprx".format(os.path.dirname(__file__)))


@pytest.fixture(scope="module")
def map_doc_a():
    map_doc = arcpyext.mapping.open_document(MAP_A_PATH)
    yield map_doc
    del map_doc


@pytest.mark.parametrize(("layer_visibility_string", "id_visibility_dict"), [("show:2,4", {
    1: False,
    2: True,
    33: False,
    3: False,
    4: True
}), ("hide:2,4", {
    1: True,
    2: False,
    33: True,
    3: True,
    4: False
}), ("exclude:2,4", {
    1: False,
    2: False,
    33: True,
    3: True,
    4: False
}), ("include:2,4", {
    1: False,
    2: True,
    33: True,
    3: True,
    4: True
})])
def test_set_layer_visibility(map_doc_a, layer_visibility_string, id_visibility_dict):
    map = map_doc_a.listMaps()[0]  # type: Map
    map.setLayerVisibility("hide:1")  # Hide the first one to ensure include works.

    map.setLayerVisibility(layer_visibility_string)

    id_visibility_dict_to_test = {
        layer.getDefinition(get_cim_version()).serviceLayerID: layer.visible
        for layer in map.listLayers()
    }
    print(id_visibility_dict_to_test, "should equal", id_visibility_dict)
    assert id_visibility_dict_to_test == id_visibility_dict
