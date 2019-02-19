import arcpy
import arcpyext
import os
import pytest
from contextlib import contextmanager

PROJECT_PATH = os.path.abspath("{0}/../samples/test_mapping_complex.aprx".format(os.path.dirname(__file__)))
NOT_A_PROJECT_PATH = os.path.abspath("{0}/../samples/not_an_mxd.aprx".format(os.path.dirname(__file__)))

@contextmanager
def does_not_raise():
    yield

@pytest.fixture(scope="module")
def project():
    return PROJECT_PATH

@pytest.fixture(scope="module")
def not_a_project():
    return NOT_A_PROJECT_PATH

@pytest.mark.parametrize(("project", "result"), [
    (PROJECT_PATH, True),
    (NOT_A_PROJECT_PATH, False)])
def test_mxd_exists(project, result):
    output, version = arcpyext.arcobjects.project_exists(project)

    assert output == result

@pytest.mark.parametrize(("project,expectation"), [
    (PROJECT_PATH, does_not_raise()),
    (NOT_A_PROJECT_PATH, pytest.raises(Exception))])
def test_open_project(project, expectation):
    with expectation:
        project_object = arcpyext.arcobjects.open_project(project)

@pytest.mark.parametrize(("project,expectation"), [
    (PROJECT_PATH, does_not_raise()),
    (NOT_A_PROJECT_PATH, pytest.raises(Exception))])
def test_list_layers(project, expectation):
    with expectation:
        layers = arcpyext.arcobjects.list_layers(project)

        # There are 5 items in test_mapping_complex.mxd
        assert len(layers) == 5

