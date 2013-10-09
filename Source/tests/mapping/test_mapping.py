import os.path

import arcpy
import pytest

import arcpyext

MXD_PATH = os.path.normpath("{0}/samples/test_mapping.mxd".format(os.path.dirname(__file__)))
CLIP2_PATH = os.path.normpath("{0}/samples/statesp020_clip2.shp".format(os.path.dirname(__file__)))
TEST_DATA_TABLE2_PATH = os.path.normpath("{0}/samples/test_data_table2.gdb".format(os.path.dirname(__file__)))

def pytest_funcarg__map():
    return arcpy.mapping.MapDocument(MXD_PATH)

@pytest.mark.parametrize(("data_sources", "layer_data_sources_equal", "table_data_sources_equal", "raises_ex", "ex_type"), [
    ({'layers': [ { 'workspace': CLIP2_PATH }], 'dataTables': [ { 'workspace': TEST_DATA_TABLE2_PATH } ]}, [False], [False], False, None),
    ({'layers': [None], 'dataTables': [None]}, [True], [True], False, None),
    ({'layers': [], 'dataTables': []}, [True], [True], True, arcpyext.exceptions.ChangeDataSourcesError)
])
def test_change_data_sources(map, data_sources, layer_data_sources_equal, table_data_sources_equal, raises_ex, ex_type):
    layers = arcpy.mapping.ListLayers(map)
    old_data_sources = []
    print(MXD_PATH)

    data_tables = arcpy.mapping.ListTableViews(map)
    old_table_sources = []
    
    for table in data_tables:
        print table.name
        old_table_sources.append(table.dataSource)

    for layer in layers:
        old_data_sources.append(layer.dataSource)
    
    if (raises_ex):
        with pytest.raises(ex_type):
            arcpyext.mapping.change_data_sources(map, data_sources)
    else:
        arcpyext.mapping.change_data_sources(map, data_sources)

        for idx, layer in enumerate(layers):
            if layer.isGroupLayer or not layer.supports("workspacePath"):
                continue
            print layer.dataSource
            print old_data_sources[idx]
            assert (layer.dataSource == old_data_sources[idx]) == layer_data_sources_equal[idx]
        
        for idx, table in enumerate(data_tables):                
            print table.dataSource
            print old_table_sources[idx]
            assert (table.dataSource == old_table_sources[idx]) == table_data_sources_equal[idx]
            


@pytest.mark.parametrize(("file_path", "expected_output"), [
    ("D:\\blah\\foo\\bar.sde/USER.SOMEDATASET/USER.FEATURECLASS", 
        ("D:\\blah\\foo\\bar.sde/USER.SOMEDATASET/USER.FEATURECLASS", None)),
    ("D:\\blah\\foo\\bar.shp", ("D:\\blah\\foo", "bar"))
])
def test_split_arc_data_path(file_path, expected_output):
    out = arcpyext.mapping.split_arc_data_path(file_path)
    assert out == expected_output