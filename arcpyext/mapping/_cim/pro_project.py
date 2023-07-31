# coding=utf-8

# Python 2/3 compatibility
# pylint: disable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position,import-error,no-name-in-module
from __future__ import (absolute_import, division, print_function, unicode_literals)
from future.builtins.disabled import *
from future.builtins import *
from future.standard_library import install_aliases
from future.utils import raise_from
install_aliases()
# pylint: enable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position,import-error,no-name-in-module

# Standard lib imports
import zipfile

# .NET Imports
from ArcGIS.Core.CIM import CIMGISProject

# Local imports
from .helpers import read_file_in_zip
from .pro_map import ProMap


class ProProject(object):

    _cims = None
    _pro_maps = None
    _proj_zip = None

    def __init__(self, proj_file_path):
        self._proj_file_path = proj_file_path
        self._cims = {}
        self._cimmaps = {}

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, *args):
        self.close()

    #region PROPERTIES

    @property
    def maps(self):
        if not self._pro_maps:
            # get project items of type map
            cimproject_items = [i for i in self._cimgisproject.ProjectItems if i.ItemType == "Map"]

            # map paths are pre-pended with 'CIMPATH=', strip that to get the actual zip file path
            map_paths = [pi.CatalogPath[8:] for pi in cimproject_items]

            # get XML for each map in archive, create ProMap object
            self._pro_maps = [
                ProMap(self._proj_zip, read_file_in_zip(self._proj_zip, map_path)) for map_path in map_paths
            ]

        # return a shallow copy so our internal list isn't altered
        return self._pro_maps.copy()

    @property
    def _cimgisproject(self):
        if not "GISProject" in self._cims:
            # check what format support we have on ArcGIS Pro
            supports_json_proj = hasattr(CIMGISProject, "FromJson")
            supports_xml_proj = hasattr(CIMGISProject, "FromXml")

            # read project based on supported file type
            try:
                if supports_json_proj:
                    self._cims["GISProject"] = CIMGISProject.FromJson(
                        read_file_in_zip(self._proj_zip, "GISProject.json")
                    )
                elif supports_xml_proj:
                    self._cims["GISProject"] = CIMGISProject.FromXml(read_file_in_zip(self._proj_zip, "GISProject.xml"))
                else:
                    raise NotImplementedError(
                        "This version of ArcGIS Pro is unknown and supports neither XML-based or JSON-based CIM Project loading."
                    )
            except KeyError as ke:
                raise_from(
                    NotImplementedError(
                        "This version of ArcGIS Pro does not support the type of Project you are attempting to open."
                    ), ke
                )

        return self._cims["GISProject"]

    #endregion

    #region PUBLIC FUNCTIONS

    def close(self):
        if self._proj_zip:
            self._proj_zip.close()
            self._proj_zip = None

    def open(self):
        """Opens the ArcGIS Project for reading, not required when used inside a 'with' statement."""
        if not self._proj_zip:
            self._proj_zip = zipfile.ZipFile(self._proj_file_path, mode="r", allowZip64=True)

    #endregion
