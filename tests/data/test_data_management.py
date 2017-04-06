import os.path

import arcpy
import pytest

import arcpyext

CLIP2_PATH = os.path.normpath("{0}/samples/statesp020_clip2.shp".format(os.path.dirname(__file__)))

@pytest.fixture(scope="module")
def workspace():
    return os.path.normpath("{0}/samples/test_data_states.gdb".format(os.path.dirname(__file__)))

@pytest.fixture(scope="module")
def in_table(workspace):
    return "{0}/States".format(workspace)

@pytest.fixture
def edit_session(request, workspace):
    # print(workspace)
    edit = arcpy.da.Editor(workspace)
    edit.startEditing()

    def finalizer():
            edit.stopEditing(False)

    request.addfinalizer(finalizer)

    return edit

@pytest.mark.parametrize(("where_clause", "expected_count", "field_names"), [
    (None, 48, "*"),
    ("STATE = 'Michigan'", 34, "*"),
    ("STATE = 'Arizona'", 0, "*"),
    ("STATE = 'Michigan'", 34, ["STATE"])
])
def test_read_rows(in_table, where_clause, expected_count, field_names):
    rows = arcpyext.data.read_rows(in_table, where_clause, field_names)
    assert(len(rows) == expected_count)

@pytest.mark.parametrize(("where_clause", "expected_count", "field_names"), [
    (None, 0, "*"),
    ("STATE = 'Michigan'", 14, "*"),
    ("STATE = 'Arizona'", 48, "*")
])
def test_delete_rows(in_table, edit_session, where_clause, expected_count, field_names):
    arcpyext.data.delete_rows(edit_session, in_table, where_clause, field_names)
    rows = arcpyext.data.read_rows(in_table)
    assert(len(rows) == expected_count)

@pytest.mark.parametrize(("pre_edit_where", "post_edit_where", "expected_count", "field_names"), [
    ("STATE = 'Wisconsin'", "STATE = 'Wisconsin'", 0, ("STATE")),
    ("STATE = 'Wisconsin'", "STATE = 'Test'", 14, ("STATE"))
])
def test_update_rows_func(in_table, edit_session, pre_edit_where, post_edit_where, expected_count, field_names):
    def update_row(row):
        row[0] = "Test"
        return row

    arcpyext.data.update_rows_func(edit_session, in_table, update_row, pre_edit_where, field_names)
    rows = arcpyext.data.read_rows(in_table, post_edit_where)
    assert(len(rows) == expected_count)
