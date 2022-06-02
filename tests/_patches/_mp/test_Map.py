# coding=utf-8
"""This module tests for the patches module."""

import os
import sys
import arcpyext
import pytest

PYTHON_2 = sys.version_info[0] < 3

if PYTHON_2:
    MAP_A_PATH = os.path.abspath("{0}/../../samples/test_mapping_complex.mxd".format(os.path.dirname(__file__)))
else:
    MAP_A_PATH = os.path.abspath("{0}/../../samples/test_mapping_complex.aprx".format(os.path.dirname(__file__)))


@pytest.fixture(scope="module")
def map_doc_a():
    map_doc = arcpyext.mapping.open_document(MAP_A_PATH)
    yield map_doc
    del map_doc


@pytest.mark.parametrize(
    ("layer_visibility_string", "id_visibility_dict"), [
        ("show:2,4", {
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
        })
    ]
)
def test_set_layer_visibility(map_doc_a, layer_visibility_string, id_visibility_dict):
    if PYTHON_2:
        # functionality doesn't exist on Python 2, make this a null-op
        assert True
        return

    map = map_doc_a.listMaps()[0]  # type: Map
    map.setLayerVisibility("hide:1")  # Hide the first one to ensure include works.

    map.setLayerVisibility(layer_visibility_string)

    id_visibility_dict_to_test = {
        layer.getDefinition(arcpyext._patches._mp._cim_helpers.get_cim_version()).serviceLayerID: layer.visible
        for layer in map.listLayers()
    }
    print(id_visibility_dict_to_test, "should equal", id_visibility_dict)
    assert id_visibility_dict_to_test == id_visibility_dict


def test_set_layer_visibility_errors(map_doc_a):
    if PYTHON_2:
        # functionality doesn't exist on Python 2, make this a null-op
        assert True
        return

    map = map_doc_a.listMaps()[0]  # type: Map
    with pytest.raises(ValueError):
        map.setLayerVisibility("foo:1")

    with pytest.raises(Exception):
        map.setLayerVisibility("bar")