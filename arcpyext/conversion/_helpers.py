# Python 2/3 compatibility
from __future__ import (absolute_import, division, print_function, unicode_literals)
from future.builtins import *
from future.builtins.disabled import *
from future.standard_library import install_aliases
install_aliases()

import arcpy

def get_textual_fields(table):
    """Get fields of a table, filter out ones that can't be written to human-readable text."""
    all_fields = arcpy.ListFields(table)
    shape_field_names = [f.name for f in arcpy.ListFields(table, field_type = "Geometry")]
    blob_field_names = [f.name for f in arcpy.ListFields(table, field_type = "BLOB")]
    return [f for f in all_fields if f.name not in shape_field_names and f.name not in blob_field_names]