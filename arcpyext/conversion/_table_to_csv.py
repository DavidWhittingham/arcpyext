import csv

import arcpy

from ._helpers import get_textual_fields

def table_to_csv(table, output_file_path, use_field_alias_as_column_header = False):
    fields = get_textual_fields(table)

    header_attr = "name" if use_field_alias_as_column_header == False else "aliasName"
    headers = [getattr(f, header_attr) for f in fields]

    # setup csv, write column headings
    with open(output_file_path, "wb+") as csvfile:
        csvwriter = csv.writer(csvfile, dialect="excel")
        csvwriter.writerow(headers)

        # write data
        with arcpy.da.SearchCursor(table, [f.name for f in fields]) as cursor:
            for row in cursor:
                csvwriter.writerow(row)