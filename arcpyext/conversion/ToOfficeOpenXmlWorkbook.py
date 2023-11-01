# coding=utf-8
"""Class for commonalities in the conversion process."""

# Python 2/3 compatibility
# pylint: disable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position
from __future__ import (absolute_import, division, print_function, unicode_literals)
from future.builtins.disabled import *
from future.builtins import *
from future.standard_library import install_aliases
install_aliases()
# pylint: enable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position

# Standard library imports
import sys

from io import BytesIO

# Third-party imports
import arcpy
import xlsxwriter

from pathlib2 import Path

# Local imports
from ._ConvertBase import ConvertBase
from ._helpers import get_textual_fields


class ToOfficeOpenXmlWorkbook(ConvertBase):

    #region Public overrides

    def feature_class(self, input_fc, output_workbook, use_field_alias_as_column_header=False):
        if not arcpy.Exists(input_fc):
            raise ValueError("input_fc does not exist.")

        output_workbook = Path(output_workbook).resolve()

        if output_workbook.exists():
            raise ValueError("output_workbook already exists.")

        # get input feature class description for copy process
        input_fc_desc = arcpy.Describe(input_fc)

        if not input_fc_desc.dataType == "FeatureClass":
            raise ValueError("input_fc is not of type 'FeatureClass'.")

        output_workbook = xlsxwriter.Workbook(str(output_workbook))

        sheet_name = self._feature_class_default_name(input_fc_desc, output_workbook)

        self._feature_class(input_fc_desc, output_workbook, sheet_name, use_field_alias_as_column_header)

        output_workbook.close()

        del input_fc_desc
        arcpy.management.ClearWorkspaceCache()

    def table(self, input_table, output_workbook, use_field_alias_as_column_header=False):
        if not arcpy.Exists(input_table):
            raise ValueError("input_table does not exist.")

        output_workbook = Path(output_workbook).resolve()

        if output_workbook.exists():
            raise ValueError("output_table already exists.")

        # get input feature class description for copy process
        input_table_desc = arcpy.Describe(input_table)

        if not input_table_desc.dataType == "Table":
            raise ValueError("input_table is not of type 'Table'.")

        output_workbook = xlsxwriter.Workbook(str(output_workbook))

        sheet_name = self._table_default_name(input_table_desc, output_workbook)

        self._table(input_table_desc, output_workbook, sheet_name, use_field_alias_as_column_header)

        output_workbook.close()

        del input_table_desc
        arcpy.management.ClearWorkspaceCache()

    def relationship_class(self, input_rel, output_rel):
        return super().relationship_class(input_rel, output_rel)

    def workspace(self, input_workspace, output_path, use_field_alias_as_column_header=False):
        if not arcpy.Exists(input_workspace):
            raise ValueError("input_workspace does not exist.")

        input_workspace_desc = arcpy.Describe(input_workspace)

        if not input_workspace_desc.dataType == "Workspace":
            raise ValueError("input_workspace is not of type 'Workspace'.")

        # get output_path as a Path object
        output_path = Path(output_path).resolve()

        output_workbook = self._create_output_workspace(
            output_path, use_field_alias_as_column_header=use_field_alias_as_column_header
        )

        for c in input_workspace_desc.children:
            if c.dataType == 'FeatureClass':
                self._feature_class(
                    c,
                    output_workbook,
                    self._feature_class_default_name(c, output_workbook),
                    use_field_alias_as_column_header=use_field_alias_as_column_header
                )
            elif c.dataType == 'Table':
                self._table(
                    c,
                    output_workbook,
                    self._table_default_name(c, output_workbook),
                    use_field_alias_as_column_header=use_field_alias_as_column_header
                )
            elif c.dataType == 'RelationshipClass':
                self._relationship_class(
                    c,
                    self._relationship_class_default_name(c, output_path),
                    use_field_alias_as_column_header=use_field_alias_as_column_header
                )

        output_workbook.close()

        del input_workspace_desc
        arcpy.management.ClearWorkspaceCache()

    #endregion

    #region Private overrides

    def _create_output_workspace(self, output_path, **kwargs):

        # create directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)
        return xlsxwriter.Workbook(str(output_path))

    def _feature_class(self, desc, output_workbook, sheet_name, use_field_alias_as_column_header):
        self._dataset_to_ooxml(desc.catalogPath, output_workbook, sheet_name, use_field_alias_as_column_header)

    def _feature_class_default_name(self, desc, output_workbook, **kwargs):
        """
        Creates a Path object representing the full path of an output feature class in the comma-separated-values format.
        """
        return self._get_default_name(desc, output_workbook)

    def _table(self, desc, output_workbook, sheet_name, use_field_alias_as_column_header):
        self._dataset_to_ooxml(desc.catalogPath, output_workbook, sheet_name, use_field_alias_as_column_header)

    def _table_default_name(self, desc, output_workbook, **kwargs):
        """
        Creates a Path object representing the full path of an output table in the comma-separated-values format.
        """
        return self._get_default_name(desc, output_workbook)

    def _relationship_class_default_name(self, desc, output_workspace, **kwargs):
        """
        Creates a Path object representing the full path of an output feature class in whatever the destination format is.
        """
        # Output path will be a GeoPackage, have to get the parent folder
        return output_workspace.parent.joinpath(desc.name + ".txt")

    #endregion

    #region Private functions

    def _dataset_to_ooxml(self, dataset, workbook, sheet_name, use_field_alias_as_column_header):
        worksheet = workbook.add_worksheet(sheet_name)

        fields = get_textual_fields(dataset, include_geometry=True)

        # get fields, including shape as well-known text, write data to spreadsheet
        field_names = [f.name + "@WKT" if f.type == "Geometry" else f.name for f in fields]
        row_no = 0
        with arcpy.da.SearchCursor(dataset, field_names) as cursor:
            for row in cursor:
                row_no += 1
                worksheet.write_row(row_no, 0, row)

        # create table layout, if any data was written
        if row_no > 0:
            header_attr = "name" if use_field_alias_as_column_header == False else "aliasName"
            worksheet.add_table(
                0, 0, row_no - 1,
                len(fields) - 1, {"columns": [{
                    "header": getattr(f, header_attr)
                } for f in fields]}
            )

    def _get_default_name(self, desc, output_workbook, **kwargs):
        # get the default name for OOXML, respecting the 31 character limit and avoiding collisions

        name = desc.name

        if len(name) > 31:
            name = name[:31]

        worksheet = output_workbook.get_worksheet_by_name(name)

        if worksheet != None:
            # worksheet with that name already exists, generate a name that doesn't
            i = 1
            while True:
                test_name = "{}~{}".format(name[:31 - (1 + len(str(i)))], str(i))
                worksheet = output_workbook.get_worksheet_by_name(test_name)
                if worksheet != None:
                    name = test_name
                    break

        return name

    #endregion