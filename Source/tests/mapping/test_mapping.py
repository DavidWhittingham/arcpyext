import os.path

import arcpy
import pytest

import arcpyext

MXD_PATH = os.path.abspath("./mapping/samples/test_mapping.mxd")
CLIP2_DATA_SOURCE = { "workspacePath": os.path.abspath("./mapping/samples/"), "datasetName": "statesp020_clip2" }
TEST_DATA_SOURCE = { "workspacePath": os.path.abspath("./mapping/samples/test_data_table2.gdb") }

def pytest_funcarg__map():
    print("MXD: " + MXD_PATH)
    return arcpy.mapping.MapDocument(MXD_PATH)

@pytest.mark.parametrize(("data_sources", "layer_data_sources_equal", "table_data_sources_equal", "raises_ex", "ex_type"), [
    ({'layers': [[ CLIP2_DATA_SOURCE ]], 'tableViews': [ TEST_DATA_SOURCE ]}, [False], [False], False, None),
    ({'layers': [[None]], 'tableViews': [None]}, [True], [True], False, None),
    ({'layers': [], 'tableViews': []}, [True], [True], True, arcpyext.exceptions.ChangeDataSourcesError)
])
def test_change_data_sources(map, data_sources, layer_data_sources_equal, table_data_sources_equal, raises_ex, ex_type):
    layers = arcpy.mapping.ListLayers(map)
    old_data_sources = []

    for layer in layers:
        old_data_sources.append(layer.dataSource)

    data_tables = arcpy.mapping.ListTableViews(map)
    old_table_sources = []
    
    for table in data_tables:
        print table.name
        old_table_sources.append(table.dataSource)

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