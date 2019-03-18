import os.path
import json
import arcpy
import pytest
import arcpyext

TEST_DATA_SOURCE = {"workspacePath": os.path.abspath(
    "{0}/../samples/test_data_table2.gdb".format(os.path.dirname(__file__)))}
BROKEN_DATA_SOURCE = {"workspacePath": os.path.abspath(
    "{0}/../samples/test_data_table99.gdb".format(os.path.dirname(__file__)))}
CLIP2_DATA_SOURCE = {"workspacePath": os.path.abspath(
    "{0}/../samples/".format(os.path.dirname(__file__))), "datasetName": "statesp020_clip2"}
PROJECT_PATH = os.path.abspath("{0}/../samples/test_mapping.aprx".format(os.path.dirname(__file__)))
PROJECT_COMPLEX_PATH = os.path.abspath("{0}/samples/test_mapping_complex.aprx".format(os.path.dirname(__file__)))
PROJECT_COMPLEX_B_PATH = os.path.abspath("{0}/samples/test_mapping_complex_b.aprx".format(os.path.dirname(__file__)))

@pytest.fixture(scope="module")
def project():
    return arcpy.mp.ArcGISProject(PROJECT_PATH)
            
@pytest.mark.parametrize(("data_sources", "layer_data_sources_equal", "table_data_sources_equal", "raises_ex", "ex_type"), [
    ({'layers': [[CLIP2_DATA_SOURCE]], 'tableViews': [
     TEST_DATA_SOURCE]}, [False], [False], False, None),
    ({'layers': [[None]], 'tableViews': [None]}, [True], [True], False, None),
    ({'layers': [], 'tableViews': []}, [True], [True],
     True, arcpyext.exceptions.ChangeDataSourcesError),
     ({'tableViews': [None]}, [True], [True],
     True, arcpyext.exceptions.ChangeDataSourcesError),
     ({'tableViews': [None, None, None]}, [True], [True],
     True, arcpyext.exceptions.ChangeDataSourcesError)
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
            arcpyext.mp.change_data_sources(project, data_sources)
    else:
        arcpyext.mp.change_data_sources(project, data_sources)

        for idx, layer in enumerate(layers):
            if layer.isGroupLayer or not layer.supports("workspacePath"):
                continue
            assert (layer.dataSource ==
                    old_data_sources[idx]) == layer_data_sources_equal[idx]

        for idx, table in enumerate(data_tables):
            assert (table.dataSource ==
                    old_table_sources[idx]) == table_data_sources_equal[idx]

@pytest.mark.parametrize(("mxd", "raises_ex", "ex_type"), [
    (PROJECT_COMPLEX_PATH, False, None)])
def test_list_document_data_sources(mxd, raises_ex, ex_type):
    map = arcpy.mp.ArcGISProject(mxd)
    result = arcpyext.mp.list_document_data_sources(map)
    """# print(json.dumps(result))

    # Expecting:
    # {
    #     "layers": [
    #         [
    #           {
    #             "datasetName": "statesp020_clip1",
    #             "workspacePath": "G:\\LARIE\\AutoPublish\\arcpyext\\tests\\samples",
    #             "name": "Layer 1",
    #             "dataSource": "G:\\LARIE\\AutoPublish\\arcpyext\\tests\\samples\\statesp020_clip1.shp",
    #             "longName": "Layer 1"
    #           },
    #           {
    #             "datasetName": "statesp020_clip1",
    #             "workspacePath": "G:\\LARIE\\AutoPublish\\arcpyext\\tests\\samples",
    #             "name": "Layer 2 (Duplicated)",
    #             "dataSource": "G:\\LARIE\\AutoPublish\\arcpyext\\tests\\samples\\statesp020_clip1.shp",
    #             "longName": "Layer 2 (Duplicated)"
    #           },
    #           "None",             // This is a group layer
    #           {
    #             "datasetName": "statesp020_clip1",
    #             "workspacePath": "G:\\LARIE\\AutoPublish\\arcpyext\\tests\\samples",
    #             "name": "Layer 3 (Nested)",
    #             "dataSource": "G:\\LARIE\\AutoPublish\\arcpyext\\tests\\samples\\statesp020_clip1.shp",
    #             "longName": "New Group Layer\\Layer 3 (Nested)"
    #           }
#           ]
    #     ],
    #     "tableViews: [{'definitionQuery': u'', 'datasetName': u'statesp020.txt', 'dataSource': u'G:\\LARIE\\AutoPublish\\arcpyext\\tests\\samples\\statesp020.txt', 'workspacePath': u'G:\\LARIE\\AutoPublish\\arcpyext\\tests\\samples'}]}]
    # }"""

    # Number of maps in the project
    assert len(result['layers']) == 1

    # Dataframe 1
    assert len(result['layers'][0]) == 5, "Layer count"

    # 'id' and 'datasetName' comes from from _arcobjects. Assertions removed for now

    # Layer 1
    #assert result['layers'][0][0]['id'] == 1
    assert result['layers'][0][0]['name'] == "Layer 1"
    #assert result['layers'][0][0]['datasetName'] == "statesp020_clip1"

    # Layer 2
    #assert result['layers'][0][1]['id'] == 2
    assert result['layers'][0][1]['name'] == "Layer 2"
    #assert result['layers'][0][1]['datasetName'] == "statesp020_clip2"

    # Layer 3
    #assert result['layers'][0][3]['id'] == 3
    assert result['layers'][0][3]['name'] == "Layer 3"
    #assert result['layers'][0][3]['datasetName'] == "statesp020_clip1"

    # Tables
    assert len(result['tableViews']) == 1

@pytest.mark.parametrize(("mxd_a", "mxd_b", "data_frame_updates", "layers_added", "layers_updated", "layers_removed", "raises_ex", "ex_type"), [
    (PROJECT_COMPLEX_PATH, PROJECT_COMPLEX_B_PATH, 2, 1, 2, 1, False, None)
])
def test_compare_map_documents(mxd_a, mxd_b, data_frame_updates, layers_added, layers_updated, layers_removed, raises_ex, ex_type):
    a = arcpy.mp.ArcGISProject(mxd_a)
    b = arcpy.mp.ArcGISProject(mxd_b)
    result = arcpyext.mp.compare(a, b)

    data_frame_changes = result['dataFrames']
    layer_changes = result['layers']

    #assert len(data_frame_changes) == data_frame_updates, "Expected {0} data frame updates".format(data_frame_updates)
    assert len(layer_changes['added']) == layers_added, "Expected {0} a".format(layers_added)
    #assert len(layer_changes['updated']) == layers_updated, "Expected {0} u".format(layers_updated)
    assert len(layer_changes['removed']) == layers_removed, "Expected {0} d".format(layers_removed)