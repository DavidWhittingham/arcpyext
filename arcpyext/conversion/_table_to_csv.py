# Python 2/3 compatibility
from __future__ import (absolute_import, division, print_function, unicode_literals)
from future.builtins import *
from future.builtins.disabled import *
from future.standard_library import install_aliases
install_aliases()

import csv

import arcpy

from ._helpers import get_textual_fields

def table_to_csv(table, output_file_path, use_field_alias_as_column_header = False):
    fields = get_textual_fields(table)

    header_attr = "name" if use_field_alias_as_column_header == False else "aliasName"
    headers = [getattr(f, header_attr) for f in fields]

    # setup csv, write column headings
    with open(output_file_path, "w") as csvfile:
        csvwriter = csv.writer(csvfile, dialect="excel")
        csvwriter.writerow(headers)

        # write data
        with arcpy.da.SearchCursor(table, [f.name for f in fields]) as cursor:
            for row in cursor:
                csvwriter.writerow(row)