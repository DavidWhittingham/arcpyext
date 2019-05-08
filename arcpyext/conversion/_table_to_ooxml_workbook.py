# coding=utf-8
"""This module converts tables to OOXML (Excel) format."""

# Python 2/3 compatibility
# pylint: disable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position
from __future__ import (absolute_import, division, print_function, unicode_literals)
from future.builtins.disabled import *
from future.builtins import *
from future.standard_library import install_aliases
install_aliases()
# pylint: enable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position

# Third-party imports
import arcpy
import xlsxwriter

# Local imports
from ._helpers import get_textual_fields

def table_to_ooxml_workbook(table, output_file_path, use_field_alias_as_column_header = False):
    fields = get_textual_fields(table)

    # setup workbook, write column headings
    workbook = xlsxwriter.Workbook(output_file_path)
    worksheet = workbook.add_worksheet()

    # write data
    with arcpy.da.SearchCursor(table, [f.name for f in fields]) as cursor:
        row_no = 1
        for row in cursor:
            worksheet.write_row(row_no, 0, row)
            row_no += 1

    # create table layout
    header_attr = "name" if use_field_alias_as_column_header == False else "aliasName"
    worksheet.add_table(0, 0, row_no - 1, len(fields) - 1, {
        "columns": [{"header": getattr(f, header_attr)} for f in fields]
    })

    workbook.close()