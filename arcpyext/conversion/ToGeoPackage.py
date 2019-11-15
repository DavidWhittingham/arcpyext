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

from pathlib2 import Path

# Local imports
from ._ConvertBase import ConvertBase


class ToGeoPackage(ConvertBase):
    #region Public overrides

    def feature_class(self, input_fc, output_fc):
        super().feature_class(input_fc, output_fc)
        self._clear_file_locks(Path(output_fc).parent)

    def table(self, input_table, output_table):
        super().table(input_table, output_table)
        self._clear_file_locks(Path(output_table).parent)

    def relationship_class(self, input_rel, output_rel):
        super().relationship_class(input_rel, output_rel)

    def workspace(self, input_workspace, output_path, version=None):
        super().workspace(input_workspace, output_path, version=version)
        self._clear_file_locks(output_path)

    #endregion

    #region Private overrides

    def _create_output_workspace(self, output_path, **kwargs):
        if output_path.exists():
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

    #region Private functions

    def _clear_file_locks(self, output_path):
        # arcpy holds a lock on the geopackage after creation.
        # Despite the documentation saying it only works with Enterprise geodatabases, running the below function
        # removes the lock, and is the only way I've found to do this (playing with the "Result" object returned from
        # the function proved fruitless - note that the documentation doesn't mention the function returning anything).
        arcpy.ClearWorkspaceCache_management(str(output_path))

    #endregion