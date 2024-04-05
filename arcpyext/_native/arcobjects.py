# coding=utf-8
"""
This module contains functionality for accessing ArcObjects from Python
"""

# Python 2/3 compatibility
# pylint: disable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position
from __future__ import (absolute_import, division, print_function, unicode_literals)
from future.builtins.disabled import *
from future.builtins import *
from future.standard_library import install_aliases
install_aliases()
# pylint: enable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position

# Standard lib imports
import logging
import os
import sys
import winreg

# Third-party imports
import clr

# Local imports
from ._dotnet import find_gac_assembly_path


def cast_obj(obj, ao_interface):
    """Casts obj to interface and returns comtypes POINTER or None"""

    logger = _get_logger()

    try:
        if obj == None:
            # no object provided
            return None

        # check if interface is assignable
        if not clr.GetClrType(ao_interface).IsInstanceOfType(obj):
            # can't be casted to given interface
            return None

        # Object can be casted
        return ao_interface(obj)
    except TypeError as te:
        logger.exception("An error occurred casting an object to an ArcObjects interface.", exc_info=True)
        return None

def create_obj(ao_class, ao_interface):
    """Creates a new comtypes POINTER object where ao_class is the class to be instantiated, ao_interface is the 
    interface to be assigned."""

    logger = _get_logger()

    try:
        return ao_interface(ao_class())
    except TypeError as te:
        logger.exception("An error creating an ArcObjects object and/or casting it to an interface.", exc_info=True)
        return None

def _bootstrap():
    """Initialise the Python environment to be ready to get ArcGIS Pro SDK modules."""

    # Add .NET references
    clr.AddReference(find_gac_assembly_path("ESRI.ArcGIS.System"))
    clr.AddReference(find_gac_assembly_path("ESRI.ArcGIS.Carto"))
    clr.AddReference(find_gac_assembly_path("ESRI.ArcGIS.Geodatabase"))
    clr.AddReference(find_gac_assembly_path("ESRI.ArcGIS.Geometry"))
    clr.AddReference(find_gac_assembly_path("ESRI.ArcGIS.NetworkAnalyst"))

def _get_logger():
    return logging.getLogger("arcpyext.native")


_bootstrap()
