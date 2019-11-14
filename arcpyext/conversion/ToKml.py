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


class ToKml(ToCsvBase):

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
        arcpy.MakeFeatureLayer_management(desc.catalogPath, 'kml_layer')
        arcpy.LayerToKML_conversion('kml_layer', str(output_fc), 0)
        arcpy.Delete_management("kml_layer")

    def _feature_class_default_name(self, desc, output_workspace, **kwargs):
        """
        Creates a Path object representing the full path of an output feature class in the KML/KMZ format.
        """
        return output_workspace.joinpath(desc.name + ".kmz")

    #endregion