import os.path
import arcpy
import pytest
import arcpyext

@pytest.fixture(scope="module")
def in_gdb():
    return os.path.normpath("{0}/input/input.gdb".format(os.path.dirname(__file__)))

@pytest.fixture(scope="module")
def out_file():
    return os.path.normpath("{0}/output/output.json".format(os.path.dirname(__file__)))

@pytest.fixture(scope="module")
def in_file():
    return os.path.normpath("{0}/output/output.json".format(os.path.dirname(__file__)))

@pytest.fixture(scope="module")
def out_gdb():
    return os.path.normpath("{0}/output/output.gdb".format(os.path.dirname(__file__)))

# @pytest.mark.parametrize(("in_filter"), [
#     "*"
# ])
def test_to_json(in_gdb, out_file):
    arcpyext.schema.to_json(in_gdb, out_file)
    assert(1==1)

def test_to_gdb(in_file, out_gdb):
    arcpyext.schema.to_gdb(in_file, out_gdb)
    assert(1==1)
