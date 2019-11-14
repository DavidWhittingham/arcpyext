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

# Third-party imports
import arcpy

# Local imports
from ._ToCsvBase import ToCsvBase


class ToGeoPackage(ToCsvBase):
    #region Public overrides

    def feature_class(self, input_fc, output_fc, version=None):
        return super().feature_class(input_fc, output_fc, version=version)

    def table(self, input_table, output_table):
        return super().table(input_table, output_table)

    def relationship_class(self, input_rel, output_rel):
        return super().relationship_class(input_rel, output_rel)

    def workspace(self, input_workspace, output_path, version=None):
        return super().workspace(input_workspace, output_path, version=version)

    #endregion

    #region Private overrides

    def _create_output_workspace(self, output_path, **kwargs):
        if arcpy.Exists(str(output_path)):
            raise ValueError("Cannot create GeoPackage workspace, it already exists.")

        # create parent directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)

        spatial_type = "GEOPACKAGE" if kwargs["version"] == None else "GEOPACKAGE_{}".format(kwargs["version"])
        arcpy.CreateSQLiteDatabase_management(str(output_path), spatial_type)

    def _feature_class(self, desc, output_fc, **kwargs):
        arcpy.FeatureClassToFeatureClass_conversion(desc.catalogPath, str(output_fc.parent), str(output_fc.name))

    def _feature_class_default_name(self, desc, output_workspace, **kwargs):
        """
        Creates a Path object representing the full path of an output feature class in the GeoPackage format.
        """
        return output_workspace.joinpath(desc.name)

    def _table(self, desc, output_table, **kwargs):
        arcpy.TableToTable_conversion(desc.catalogPath, str(output_table.parent), str(output_table.name))

    def _table_default_name(self, desc, output_workspace, **kwargs):
        """
        Creates a Path object representing the full path of an output table in the GeoPackage format.
        """
        return output_workspace.joinpath(desc.name)

    def _relationship_class_default_name(self, desc, output_workspace, **kwargs):
        """
        Creates a Path object representing the full path of an output feature class in whatever the destination format is.
        """
        # Output path will be a GeoPackage, have to get the parent folder
        return output_workspace.parent.joinpath(desc.name + ".txt")

    #endregion