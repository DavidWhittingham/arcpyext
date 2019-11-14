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
import csv
import sys

# Third-party imports
import arcpy

# Local imports
from ._ConvertBase import ConvertBase
from ._helpers import get_textual_fields


class ToCsvBase(ConvertBase):

    #region Private overrides

    def _create_output_workspace(self, output_path, **kwargs):

        # create directory if it doesn't exist
        output_path.mkdir(parents=True, exist_ok=True)

    def _feature_class(self, desc, output_fc, **kwargs):
        self._dataset_to_csv(desc.catalogPath, output_fc, **kwargs)

    def _feature_class_default_name(self, desc, output_workspace, **kwargs):
        """
        Creates a Path object representing the full path of an output feature class in the comma-separated-values format.
        """
        return output_workspace.joinpath(desc.name + ".csv")

    def _table(self, desc, output_table, **kwargs):
        self._dataset_to_csv(desc.catalogPath, output_table, **kwargs)

    def _table_default_name(self, desc, output_workspace, **kwargs):
        """
        Creates a Path object representing the full path of an output table in the comma-separated-values format.
        """
        return output_workspace.joinpath(desc.name + ".csv")

    #endregion

    #region Private functions

    def _dataset_to_csv(self, dataset, output_file_path, **kwargs):
        use_field_alias_as_column_header = kwargs.pop("use_field_alias_as_column_header", False)

        if not arcpy.Exists(dataset):
            raise ValueError("Input dataset does not exist.")

        fields = get_textual_fields(dataset)

        header_attr = "name" if use_field_alias_as_column_header == False else "aliasName"
        headers = [getattr(f, header_attr) for f in fields]

        # setup csv, write column headings
        if sys.version_info[0] < 3:
            headers = [str(s).encode("utf-8") for s in headers]
            infile = open(str(output_file_path), 'wb')
        else:
            infile = open(str(output_file_path), 'w', newline='', encoding='utf-8')

        with infile as csvfile:
            csvwriter = csv.writer(csvfile, dialect="excel")
            csvwriter.writerow(headers)

            # write data
            with arcpy.da.SearchCursor(dataset, [f.name for f in fields]) as cursor:
                for row in cursor:
                    if sys.version_info[0] < 3:
                        csvwriter.writerow([str(s).encode("utf-8") for s in row])
                    else:
                        csvwriter.writerow(row)

    #endregion