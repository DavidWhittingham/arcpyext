# coding=utf-8
"""This module tests for the mapping module."""

# Python 2/3 compatibility
# pylint: disable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position
from __future__ import (absolute_import, division, print_function, unicode_literals)
from future.builtins.disabled import *
from future.builtins import *
from future.standard_library import install_aliases
install_aliases()
# pylint: enable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position

# Standard libary imports
import os.path
import json
import sys

# Third party imports
import arcpy
import pytest

# Local import
import arcpyext

if sys.version_info[0] < 3:
    MAP_A_PATH = os.path.abspath("{0}/../samples/test_mapping_complex.mxd".format(os.path.dirname(__file__)))
    MAP_B_PATH = os.path.abspath("{0}/../samples/test_mapping_complex_b.mxd".format(os.path.dirname(__file__)))
    ALT_LAYER_DATA_SOURCE = {
        "workspacePath": os.path.abspath("{0}/../samples/".format(os.path.dirname(__file__))),
        "datasetName": "statesp020_clip2"
    }
    ALT_TABLE_DATA_SOURCE = {
        "workspacePath": os.path.abspath("{0}/../samples/test_data_table2.gdb".format(os.path.dirname(__file__)))
    }
else:
    MAP_A_PATH = os.path.abspath("{0}/../samples/test_mapping_complex.aprx".format(os.path.dirname(__file__)))
    MAP_B_PATH = os.path.abspath("{0}/../samples/test_mapping_complex_b.aprx".format(os.path.dirname(__file__)))
    ALT_LAYER_DATA_SOURCE = {
        'connectionProperties': {
            'dataset': 'statesp020_clip1.shp',
            'workspace_factory': 'Shape File',
            'connection_info': {
                'database': os.path.abspath("{0}/../samples/".format(os.path.dirname(__file__)))
            }
        }
    }
    ALT_TABLE_DATA_SOURCE = {
        'connectionProperties': {
            'dataset': 'DataTableTest',
            'workspace_factory': 'File Geodatabase',
            'connection_info': {
                'database': '{0}/../samples/test_data_table1.gdb'.format(os.path.dirname(__file__))
            }
        }
    }


@pytest.fixture(scope="module")
def map_doc_a():
    map_doc = arcpyext.mapping.open_document(MAP_A_PATH)
    yield map_doc
    del map_doc


@pytest.fixture(scope="module")
def map_doc_b():
    map_doc = arcpyext.mapping.open_document(MAP_B_PATH)
    yield map_doc
    del map_doc


#yapf: disable
@pytest.mark.parametrize(
    ("data_sources", "layer_data_sources_equal", "table_data_sources_equal", "raises_ex", "ex_type"),
    [
        (
            [
                {
                    'layers': [ALT_LAYER_DATA_SOURCE, None, None, ALT_LAYER_DATA_SOURCE, ALT_LAYER_DATA_SOURCE],
                    'tables': [ALT_TABLE_DATA_SOURCE]
                }
            ],
            [False, True, None, False, False],
            [False],
            False,
            None
        ),
        (
            [
                {
                    'layers': [None, None, None, None, None],
                    'tables': [None]
                }
            ],
            [True, True, None, True, True],
            [True],
            False,
            None
        ),
        (
            [
                {
                    'layers': [],
                    'tables': []
                }
            ],
            [True],
            [True],
            True,
            arcpyext.exceptions.ChangeDataSourcesError
        )
    ]
)
#yapf: enable
def test_change_data_sources(map_doc_a, data_sources, layer_data_sources_equal, table_data_sources_equal, raises_ex,
                             ex_type):
    # Get layers, Python 2 or 3
    layers = map_doc_a.listLayers() if hasattr(map_doc_a, "listLayers") else arcpy.mapping.ListLayers(map_doc_a)

    old_data_sources = []

    for layer in layers:
        old_data_sources.append(layer.dataSource if layer.supports("dataSource") else None)

    # Get table views, Python 2 or 3
    data_tables = map_doc_a.listTables() if hasattr(map_doc_a,
                                                    "listTables") else arcpy.mapping.ListTableViews(map_doc_a)
    old_table_sources = []

    for table in data_tables:
        old_table_sources.append(table.dataSource)

    if (raises_ex):
        with pytest.raises(ex_type):
            arcpyext.mapping.change_data_sources(map_doc_a, data_sources)
    else:
        arcpyext.mapping.change_data_sources(map_doc_a, data_sources)

        for idx, layer in enumerate(layers):
            if layer.isGroupLayer or not layer.supports("dataSource"):
                continue
            assert (layer.dataSource == old_data_sources[idx]) == layer_data_sources_equal[idx]

        for idx, table in enumerate(data_tables):
            assert (table.dataSource == old_table_sources[idx]) == table_data_sources_equal[idx]


@pytest.mark.parametrize(("raises_ex", "ex_type"), [(False, None)])
def test_describe(map_doc_a, raises_ex, ex_type):
    result = arcpyext.mapping.describe(map_doc_a)

    # Dataframes
    assert len(result["maps"]) == 1

    # Dataframe 1
    assert len(result["maps"][0]["layers"]) == 5, "Layer count"

    # Layer 1
    assert result["maps"][0]["layers"][0]["serviceId"] == 1
    assert result["maps"][0]["layers"][0]["name"] == "Layer 1"
    assert result["maps"][0]["layers"][0]["datasetName"] == "statesp020_clip1"

    # Layer 2
    assert result["maps"][0]["layers"][1]["serviceId"] == 2
    assert result["maps"][0]["layers"][1]["name"] == "Layer 2"
    assert result["maps"][0]["layers"][1]["datasetName"] == "statesp020_clip2"

    # Layer 3
    assert result["maps"][0]["layers"][3]["serviceId"] == 3
    assert result["maps"][0]["layers"][3]["name"] == "Layer 3"
    assert result["maps"][0]["layers"][3]["datasetName"] == "statesp020_clip1"

    # Tables
    assert len(result["maps"][0]["tables"]) == 1


@pytest.mark.parametrize(("expected_document_changes", "expected_first_map_changes", "layers_added", "layers_updated",
                          "layers_removed", "raises_ex", "ex_type"), [(0, 1, 1, 2, 1, False, None)])
def test_compare_map_documents(map_doc_a, map_doc_b, expected_document_changes, expected_first_map_changes,
                               layers_added, layers_updated, layers_removed, raises_ex, ex_type):
    result = arcpyext.mapping.compare(map_doc_a, map_doc_b)

    actual_document_changes = result["document"]
    actual_first_map_changes = result["maps"][0]["map"]
    layer_changes = result["maps"][0]["layers"]

    count_actual_map_changes = len(actual_first_map_changes)

    print("Actual map changes: {}".format(count_actual_map_changes))
    print(result["maps"][0]["map"])

    assert len(actual_document_changes) == expected_document_changes, "Expected {0} document changes".format(
        expected_document_changes)
    assert len(actual_first_map_changes) == expected_first_map_changes, "Expected {} data frame updates, got {}".format(
        expected_first_map_changes, actual_first_map_changes)
    assert len(layer_changes["added"]) == layers_added, "Expected {0} a".format(layers_added)
    assert len(layer_changes["updated"]) == layers_updated, "Expected {0} u".format(layers_updated)
    assert len(layer_changes["removed"]) == layers_removed, "Expected {0} d".format(layers_removed)


@pytest.mark.parametrize(("data_source_templates"), [([{
    "dataSource": {
        "datasetName": "statesp020_clip2"
    },
    "matchCriteria": {
        "datasetName": "STATESP020_CLIP1"
    }
}])])
def test_create_replacement_data_sources_list(map_doc_a, data_source_templates):
    arcpyext.mapping.create_replacement_data_sources_list(map_doc_a, data_source_templates)


def test_map_is_valid(map_doc_a):
    #TODO: Test this function. Input is map object
    pass
