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
from ._ToCsvBase import ToCsvBase


class ToMapInfoTab(ToCsvBase):

    _licence_handler = None

    #region Public overrides

    def feature_class(self, input_fc, output_fc):
        return super().feature_class(input_fc, output_fc)

    def table(self, input_table, output_table):
        return super().table(input_table, output_table)

    def relationship_class(self, input_rel, output_rel):
        return super().relationship_class(input_rel, output_rel)

    def workspace(self, input_workspace, output_path):
        # override to wrap in extension checkout
        with _ArcGisExtension("DataInteroperability") as licence_handler:
            self._licence_handler = licence_handler
            super().workspace(input_workspace, output_path)

        self._licence_handler = None

    #endregion

    def _create_output_workspace(self, output_path, **kwargs):

        # create directory if it doesn't exist
        output_path.mkdir(parents=True, exist_ok=True)

    def _feature_class(self, desc, output_fc, **kwargs):
        if self._licence_handler != None and self._licence_handler.is_licenced:
            self._feature_class_export(desc, output_fc, **kwargs)
        else:
            with _ArcGisExtension("DataInteroperability"):
                self._feature_class_export(desc, output_fc, **kwargs)

    def _feature_class_export(self, desc, output_fc, **kwargs):
        arcpy.QuickExport_interop(desc.catalogPath, "MITAB," + str(output_fc))

    def _feature_class_default_name(self, desc, output_workspace, **kwargs):
        """
        Creates a Path object representing the full path of an output feature class in the MapInfo TAB format.
        """
        return output_workspace.joinpath(desc.name + ".tab")


class _ArcGisExtension(object):
    is_licenced = False

    def __init__(self, extension_name):
        self.extension = extension_name

    def __enter__(self):
        arcpy.CheckOutExtension(self.extension)
        self.is_licenced = True
        return self

    def __exit__(self, type, value, tb):
        arcpy.CheckInExtension(self.extension)
        self.is_licenced = False