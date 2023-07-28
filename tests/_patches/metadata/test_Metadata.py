# coding=utf-8
"""This module tests for the mapping module."""

# Python 2/3 compatibility
# pylint: disable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position
from __future__ import (absolute_import, division, print_function, unicode_literals)
from future.builtins.disabled import *
from future.builtins import *
from future.standard_library import install_aliases
install_aliases()
# pylint: enable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position

# Standard libary imports
import os.path
import sys

# Third party imports
import arcpy
import pytest

# Local import
import arcpyext

MAP_METADATA_PATH = os.path.abspath("{0}/../../samples/map_metadata.xml".format(os.path.dirname(__file__)))


@pytest.fixture(scope="module")
def map_metadata():
    map_metadata_obj = arcpy.metadata.Metadata(MAP_METADATA_PATH)
    yield map_metadata_obj
    del map_metadata_obj


@pytest.mark.skipif(sys.version_info < (3, 0), reason="requires Python 3")
@pytest.mark.parametrize(("expected_value"), [([arcpyext.TopicCategory("001")])])
def test_get_topicCategories(map_metadata, expected_value):
    assert map_metadata.topicCategories == expected_value