# coding=utf-8
"""
This module contains functionality for accessing ArcObjects from Python

Based on code from here: http://www.pierssen.com/arcgis10/python.htm
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
import ctypes
# Set the apartment state for talking to COM
ctypes.windll.ole32.CoInitialize()
import os
import sys
import winreg

# Third-party imports
import clr

def get_arcgis_pro_install_dir():
    # open the registry at HKEY_LOCAL_MACHINE
    hklm_key = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)

    try:
        # attempt to get the ArcGIS Pro installation details
        arcgis_pro_key = winreg.OpenKey(hklm_key, "SOFTWARE\\ESRI\\ArcGISPro", 0,
                                        winreg.KEY_READ | winreg.KEY_WOW64_64KEY)
        install_root = winreg.QueryValueEx(arcgis_pro_key, "InstallDir")[0]
        winreg.CloseKey(arcgis_pro_key)
    except WindowsError as we:
        raise Exception("ArcGIS Pro not installed.")
    finally:
        # close the registry
        winreg.CloseKey(hklm_key)

    return install_root

def _bootstrap():
    """Initialise the Python environment to be ready to get ArcGIS Pro SDK modules."""
    install_root = get_arcgis_pro_install_dir()
    bin_dir = os.path.join(install_root, "bin")
    extensions_dir = os.path.join(bin_dir, "Extensions")

    # search extensions directory for sub-directories
    extensions_sub_dirs = [os.path.join(extensions_dir, subdir) for subdir in next(os.walk(extensions_dir))[1]]

    # add extension directories to sys.path
    for e in extensions_sub_dirs:
        sys.path.insert(0, e)
    
    # add core bin directory
    sys.path.insert(0, bin_dir)

    # Add .NET references
    clr.AddReference("ArcGIS.Core")


_bootstrap()
