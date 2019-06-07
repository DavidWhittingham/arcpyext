# Standard lib imports
import os.path
import json

# Third-parth imports
import arcpy
import pytest

# Local imports
import arcpyext

TEST_DATA_SOURCE = {'connectionProperties': {'dataset': 'DataTableTest', 'workspace_factory': 'File Geodatabase', 
                    'connection_info': {'database': '{0}/../samples/test_data_table1.gdb'.format(os.path.dirname(__file__))}}}
CLIP_DATA_SOURCE = {'connectionProperties': {'dataset': 'statesp020_clip1.shp', 
                    'workspace_factory': 'Shape File', 
                    'connection_info': {'database': os.path.abspath("{0}/../samples/".format(os.path.dirname(__file__)))}}}
PROJECT_PATH = os.path.abspath("{0}/../samples/test_mapping.aprx".format(os.path.dirname(__file__)))
PROJECT_COMPLEX_PATH = os.path.abspath("{0}/../samples/test_mapping_complex.aprx".format(os.path.dirname(__file__)))
PROJECT_COMPLEX_B_PATH = os.path.abspath("{0}/../samples/test_mapping_complex_b.aprx".format(os.path.dirname(__file__)))

@pytest.fixture(scope="module")
def project():
    return arcpy.mp.ArcGISProject(PROJECT_PATH)
            
@pytest.mark.parametrize(("data_sources", "layer_data_sources_equal", "table_data_sources_equal", "raises_ex", "ex_type"), [
    (
        [
            {
                'layers': [CLIP_DATA_SOURCE],
                'tableViews': [TEST_DATA_SOURCE]
            }
        ],
        [False],
        [True],
        False,
        None
    ),
    (
        [
            {
                'layers': [],
                'tableViews': []
            }
        ], 
        [True],
        [True],
        True,
        arcpyext.exceptions.ChangeDataSourcesError
    ),
    (
        {'tableViews': [None]},
        [True],
        [True],
        True,
        arcpyext.exceptions.ChangeDataSourcesError
    ),
    (
        {'tableViews': [None, None, None]},
        [True],
        [True],
        True,
        arcpyext.exceptions.ChangeDataSourcesError
    )
])
def test_change_data_sources(project, data_sources, layer_data_sources_equal, table_data_sources_equal, raises_ex, ex_type):
    layers = []
    for map in project.listMaps():
        for layer in map.listLayers():
            layers.append(layer)
    old_data_sources = []

    for layer in layers:
        if layer.supports("dataSource"):
            old_data_sources.append(layer.dataSource)

    data_tables = []
    for map in project.listMaps():
        for table in map.listTables():
            data_tables.append(table)
    old_table_sources = []

    for table in data_tables:
        # print table.name
        old_table_sources.append(table.dataSource)

    if (raises_ex):
        with pytest.raises(ex_type):
            arcpyext.mapping.change_data_sources(project, data_sources)
    else:
        arcpyext.mapping.change_data_sources(project, data_sources)

        for idx, layer in enumerate(layers):
            if layer.isGroupLayer or not layer.supports("workspacePath"):
                continue
            assert (layer.dataSource ==
                    old_data_sources[idx]) == layer_data_sources_equal[idx]

        for idx, table in enumerate(data_tables):
            assert (table.dataSource ==
                    old_table_sources[idx]) == table_data_sources_equal[idx]

@pytest.mark.parametrize(("proj_path", "raises_ex", "ex_type"), [
    (PROJECT_COMPLEX_PATH, False, None)])
def test_list_document_data_sources(proj_path, raises_ex, ex_type):
    result = arcpyext.mapping.list_document_data_sources(arcpy.mp.ArcGISProject(proj_path))

    # Number of maps in the project
    assert len(result) == 1

    # Dataframe 1
    assert len(result[0]["layers"]) == 5, "Layer count"

    # "id" and "datasetName" comes from from _arcobjects. Assertions removed for now

    # Layer 1
    #assert result["layers"][0][0]["id"] == 1
    assert result[0]["layers"][0]["name"] == "Layer 1"
    assert result[0]["layers"][0]["connectionProperties"]["dataset"] == "statesp020_clip1"

    # Layer 2
    #assert result["layers"][0][1]["id"] == 2
    assert result[0]["layers"][1]["name"] == "Layer 2"
    assert result[0]["layers"][1]["connectionProperties"]["dataset"] == "statesp020_clip2"

    # Layer 3
    #assert result["layers"][0][3]["id"] == 3
    assert result[0]["layers"][3]["name"] == "Layer 3"
    assert result[0]["layers"][3]["connectionProperties"]["dataset"] == "statesp020_clip1"

    # Tables
    assert len(result[0]["tableViews"]) == 1

@pytest.mark.parametrize(("mxd_a", "mxd_b", "data_frame_updates", "layers_added", "layers_updated", "layers_removed", "raises_ex", "ex_type"), [
    (PROJECT_COMPLEX_PATH, PROJECT_COMPLEX_B_PATH, 2, 2, 2, 2, False, None)
])
def test_compare_map_documents(mxd_a, mxd_b, data_frame_updates, layers_added, layers_updated, layers_removed, raises_ex, ex_type):
    a = arcpy.mp.ArcGISProject(mxd_a)
    b = arcpy.mp.ArcGISProject(mxd_b)
    result = arcpyext.mapping.compare(a, b)

    data_frame_changes = result['dataFrames']
    layer_changes = result['layers']

    assert len(data_frame_changes) == data_frame_updates, "Expected {0} data frame updates".format(data_frame_updates)
    assert len(layer_changes['added']) == layers_added, "Expected {0} a".format(layers_added)
    assert len(layer_changes['updated']) == layers_updated, "Expected {0} u".format(layers_updated)
    assert len(layer_changes['removed']) == layers_removed, "Expected {0} d".format(layers_removed)

@pytest.mark.parametrize(("proj_path", "raises_ex", "ex_type"), [
    (PROJECT_COMPLEX_PATH, False, None)])
def test_describe_from_project(proj_path, raises_ex, ex_type):
    result = arcpyext.mapping.describe(arcpy.mp.ArcGISProject(proj_path))

    # Number of maps in the project
    assert result

@pytest.mark.parametrize(("proj_path", "raises_ex", "ex_type"), [
    (PROJECT_COMPLEX_PATH, False, None)])
def test_describe_from_path(proj_path, raises_ex, ex_type):
    result = arcpyext.mapping.describe(proj_path)

    # Number of maps in the project
    assert result

@pytest.mark.parametrize(("proj_path_a", "proj_path_b", "raises_ex", "ex_type"), [
    (PROJECT_COMPLEX_PATH, PROJECT_COMPLEX_B_PATH, False, None)])
def test_compare(proj_path_a, proj_path_b, raises_ex, ex_type):
    result = arcpyext.mapping.compare(proj_path_a, proj_path_b)

    # Number of maps in the project
    assert result