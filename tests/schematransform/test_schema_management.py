import os.path
import arcpy
import pytest
import arcpyext

@pytest.fixture(scope="module")
def in_gdb():
    return os.path.normpath("{0}/input/input.gdb".format(os.path.dirname(__file__)))

@pytest.fixture(scope="module")
def out_json():
    return os.path.normpath("{0}/output/output.json".format(os.path.dirname(__file__)))

@pytest.fixture(scope="module")
def in_json():
    return os.path.normpath("{0}/output/output.json".format(os.path.dirname(__file__)))

@pytest.fixture(scope="module")
def out_gdb():
    return os.path.normpath("{0}/output/output.gdb".format(os.path.dirname(__file__)))

@pytest.fixture(scope="module")
def out_xml():
    return os.path.normpath("{0}/output/output.xml".format(os.path.dirname(__file__)))

# @pytest.mark.parametrize(("in_filter"), [
#     "*"
# ])
def test_to_json(in_gdb, out_json):
    arcpyext.schematransform.to_json(in_gdb, out_json)
    assert(1==1)

def test_to_gdb(in_json, out_gdb):
    arcpyext.schematransform.to_gdb(in_json, out_gdb)
    assert(1==1)

def test_to_xml(in_json, out_xml):
    arcpyext.schematransform.to_xml(in_json, out_xml)
    assert(1==1)    
