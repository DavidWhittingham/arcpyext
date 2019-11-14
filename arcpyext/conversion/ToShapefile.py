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
from ._ConvertBase import ConvertBase


class ToShapefile(ConvertBase):

    #region Public overrides

    def feature_class(self, input_fc, output_fc):
        return super().feature_class(input_fc, output_fc)

    def table(self, input_table, output_table):
        return super().table(input_table, output_table)

    def relationship_class(self, input_rel, output_rel):
        return super().relationship_class(input_rel, output_rel)

    def workspace(self, input_workspace, output_path):
        return super().workspace(input_workspace, output_path)

    #endregion

    #region Private overrides

    def _create_output_workspace(self, output_path, **kwargs):

        # create directory if it doesn't exist
        output_path.mkdir(parents=True, exist_ok=True)

    def _feature_class(self, desc, output_fc, **kwargs):
        arcpy.FeatureClassToFeatureClass_conversion(desc.catalogPath, str(output_fc.parent), str(output_fc.name))

    def _feature_class_default_name(self, desc, output_workspace, **kwargs):
        """
        Creates a Path object representing the full path of an output feature class in the Shapefile format.
        """
        return output_workspace.joinpath(desc.name + ".shp")

    def _table(self, desc, output_table, **kwargs):
        arcpy.TableToTable_conversion(desc.catalogPath, str(output_table.parent), str(output_table.name))

    def _table_default_name(self, desc, output_workspace, **kwargs):
        """
        Creates a Path object representing the full path of an output table in the Shapefile format.
        """
        return output_workspace.joinpath(desc.name + ".shp")

    #endregion