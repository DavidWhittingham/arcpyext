import arcpy
import arcpyext
import os
import pytest
from contextlib import contextmanager

MXD_PATH = os.path.abspath("{0}/../samples/test_mapping_complex.mxd".format(os.path.dirname(__file__)))
NOT_AN_MXD_PATH = os.path.abspath("{0}/../samples/not_an_mxd.mxd".format(os.path.dirname(__file__)))

@contextmanager
def does_not_raise():
    yield

@pytest.fixture(scope="module")
def mxd():
    return MXD_PATH

@pytest.fixture(scope="module")
def not_an_mxd():
    return NOT_AN_MXD_PATH

@pytest.mark.parametrize(("mxd", "result"), [
    (MXD_PATH, True),
    (NOT_AN_MXD_PATH, False)])
def test_mxd_exists(mxd, result):
    output = arcpyext.arcobjects.mxd_exists(mxd)

    assert output == result

@pytest.mark.parametrize(("mxd,expectation"), [
    (MXD_PATH, does_not_raise()),
    (NOT_AN_MXD_PATH, pytest.raises(Exception))])
def test_open_mxd(mxd, expectation):
    with expectation:
        mxd_object = arcpyext.arcobjects.open_mxd(mxd)

@pytest.mark.parametrize(("mxd,expectation"), [
    (MXD_PATH, does_not_raise()),
    (NOT_AN_MXD_PATH, pytest.raises(Exception))])
def test_list_layers(mxd, expectation):
    with expectation:
        layers = arcpyext.arcobjects.list_layers(mxd)

        # There are 5 items in test_mapping_complex.mxd
        assert len(layers) == 5

