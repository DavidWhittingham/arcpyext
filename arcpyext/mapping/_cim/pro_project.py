# coding=utf-8

# Python 2/3 compatibility
# pylint: disable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position,import-error,no-name-in-module
from __future__ import (absolute_import, division, print_function, unicode_literals)
from future.builtins.disabled import *
from future.builtins import *
from future.standard_library import install_aliases
install_aliases()
from future.moves.collections import deque
from future.moves.itertools import zip_longest
from future.utils import with_metaclass
# pylint: enable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position,import-error,no-name-in-module

# Standard lib imports
import zipfile

# .NET Imports
from ArcGIS.Core.CIM import CIMGISProject

# Local imports
from .helpers import get_xml
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
            self._pro_maps = [ProMap(self._proj_zip, get_xml(self._proj_zip, map_path)) for map_path in map_paths]

        # return a shallow copy so our internal list isn't altered
        return self._pro_maps.copy()

    @property
    def _cimgisproject(self):
        if not "GISProject.xml" in self._cims:
            self._cims["GISProject.xml"] = CIMGISProject.FromXml(get_xml(self._proj_zip, "GISProject.xml"))

        return self._cims["GISProject.xml"]

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
