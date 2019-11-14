# coding=utf-8
"""This module contains helper functions related to the arcpyext.conversion module."""

# Python 2/3 compatibility
# pylint: disable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position
from __future__ import (absolute_import, division, print_function, unicode_literals)
from future.builtins.disabled import *
from future.builtins import *
from future.standard_library import install_aliases
install_aliases()
# pylint: enable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position

import arcpy


def get_textual_fields(dataset, include_geometry=False):
    """Get fields of a dataset, filter out ones that can't be written to human-readable text."""
    exclude_list = ["Blob", "Raster"]
    if not include_geometry:
        exclude_list.append("Geometry")

    return [f for f in arcpy.ListFields(dataset) if f.type not in exclude_list]