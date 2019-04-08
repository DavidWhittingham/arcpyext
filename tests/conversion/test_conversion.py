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

output_dir = os.path.normpath("{0}/output".format(os.path.dirname(__file__)))

def setup_module(module):
    """ setup any state specific to the execution of the given module."""

    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    
    os.makedirs(output_dir)

@pytest.fixture(scope="module")
def in_table():
    return os.path.normpath("{0}/input/input.gdb/TEST".format(os.path.dirname(__file__))) #TODO: Get a test table

@pytest.fixture(scope="module")
def out_csv():
    return os.path.normpath("{0}/output/output.csv".format(os.path.dirname(__file__)))

@pytest.fixture(scope="module")
def out_ooxml():
    return os.path.normpath("{0}/output/output.xlsx".format(os.path.dirname(__file__)))

def test_to_csv(in_table, out_csv):
    arcpyext.conversion.table_to_csv(in_table, out_csv)
    assert(1==1)

def test_to_ooxml(in_table, out_ooxml):
    arcpyext.conversion.table_to_ooxml_workbook(in_table, out_ooxml)
    assert(1==1)

