# Python 2/3 compatibility
# pylint: disable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position
from __future__ import (absolute_import, division, print_function, unicode_literals)
from future.builtins import *
from future.builtins.disabled import *
from future.standard_library import install_aliases
install_aliases()
# pylint: enable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position

import os
import shutil

import arcpy
import pytest

import arcpyext

from pathlib2 import Path

OUTPUT_DIR = Path(__file__).parent.joinpath("output")
TEST_INPUT_GDB_PATH = Path(__file__).parent.joinpath("input/conversion.gdb")
TEST_INPUT_COPY_GDB_PATH = Path(__file__).parent.joinpath("input/conversion.copy.gdb")
TEST_OUTPUT_PATH = Path(__file__).parent.joinpath("output")


def setup_module(module):
    """ setup any state specific to the execution of the given module."""

    if OUTPUT_DIR.exists():
        shutil.rmtree(str(OUTPUT_DIR))

    os.makedirs(str(OUTPUT_DIR))


@pytest.yield_fixture(scope="function")
def in_workspace():
    # copy, yield, and delete in order to test for Arc locking files
    shutil.copytree(str(TEST_INPUT_GDB_PATH), str(TEST_INPUT_COPY_GDB_PATH))
    yield TEST_INPUT_COPY_GDB_PATH
    shutil.rmtree(str(TEST_INPUT_COPY_GDB_PATH))


@pytest.mark.parametrize(("output_path"), [(TEST_OUTPUT_PATH.joinpath("csv"))])
def test_convert_csv(in_workspace, output_path):
    in_workspace_str = str(in_workspace)
    output_path_str = str(output_path)
    arcpyext.conversion.to_csv.workspace(in_workspace_str, output_path_str)
    assert output_path.exists()

    # check KML/KMZ exists
    assert any(child.suffix.lower() in [".csv"] for child in output_path.iterdir())


@pytest.mark.parametrize(("output_path", "version"), [(TEST_OUTPUT_PATH.joinpath("gpkg_default\\output.gpkg"), None),
                                                      (TEST_OUTPUT_PATH.joinpath("gpkg_1.0\\output.gpkg"), 1.0),
                                                      (TEST_OUTPUT_PATH.joinpath("gpkg_1.1\\output.gpkg"), 1.1),
                                                      (TEST_OUTPUT_PATH.joinpath("gpkg_1.2\\output.gpkg"), 1.2)])
def test_convert_geopackage(in_workspace, output_path, version):
    in_workspace_str = str(in_workspace)
    output_path_str = str(output_path)
    arcpyext.conversion.to_geopackage.workspace(in_workspace_str, output_path_str, version=version)
    assert output_path.exists()


@pytest.mark.parametrize(("output_path"), [(TEST_OUTPUT_PATH.joinpath("kml"))])
def test_convert_kml(in_workspace, output_path):
    in_workspace_str = str(in_workspace)
    output_path_str = str(output_path)
    arcpyext.conversion.to_kml.workspace(in_workspace_str, output_path_str)
    assert output_path.exists()

    # check KML/KMZ exists
    assert any(child.suffix.lower() in [".kml", ".kmz"] for child in output_path.iterdir())


@pytest.mark.parametrize(("output_path"), [(TEST_OUTPUT_PATH.joinpath("mapinfo"))])
def test_convert_mapinfo_tab(in_workspace, output_path):
    in_workspace_str = str(in_workspace)
    output_path_str = str(output_path)
    arcpyext.conversion.to_mapinfo_tab.workspace(in_workspace_str, output_path_str)
    assert output_path.exists()

    # check MapInfo tab file exists
    assert any(child.suffix.lower() in [".tab"] for child in output_path.iterdir())


@pytest.mark.parametrize(("output_path"), [(TEST_OUTPUT_PATH.joinpath("shp"))])
def test_convert_shapefile(in_workspace, output_path):
    in_workspace_str = str(in_workspace)
    output_path_str = str(output_path)
    arcpyext.conversion.to_shapefile.workspace(in_workspace_str, output_path_str)
    assert output_path.exists()

    # check Shapefile exists
    assert any(child.suffix.lower() in [".shp"] for child in output_path.iterdir())


@pytest.mark.parametrize(("output_path"), [(TEST_OUTPUT_PATH.joinpath("xlsx\\output.xlsx"))])
def test_convert_ooxml_workbook(in_workspace, output_path):
    in_workspace_str = str(in_workspace)
    output_path_str = str(output_path)
    arcpyext.conversion.to_ooxml_workbook.workspace(in_workspace_str, output_path_str)
    assert output_path.exists()

    # check OOXML Workbook exists
    assert any(child.suffix.lower() in [".xlsx"] for child in output_path.parent.iterdir())