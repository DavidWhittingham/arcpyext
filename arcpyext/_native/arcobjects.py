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

from contextlib import contextmanager

import comtypes

ARCGIS_COM_GUID = comtypes.GUID("{6FCCEDE0-179D-4D12-B586-58C88D26CA78}")
ESRI_REGISTRY_PATH = None
ESRI_VERSION = 10.3


@contextmanager
def licenced_context():
    init_context = _init()
    try:
        yield init_context
    finally:
        _shutdown_product(init_context)


def cast_obj(obj, interface):
    """Casts obj to interface and returns comtypes POINTER or None"""
    try:
        create_obj = obj.QueryInterface(interface)
        return create_obj
    except:
        return None


def create_obj(ao_class, ao_interface):
    """Creates a new comtypes POINTER object where ao_class is the class to be instantiated, ao_interface is the 
    interface to be assigned."""

    from comtypes.client import CreateObject
    try:
        ptr = CreateObject(ao_class, interface=ao_interface)
        return ptr
    except:
        return None


def _bootstrap():
    """Initialise all the needed base modules, ready to get a licence."""
    _get_used_ao_modules()

    from comtypes.client import GetModule
    GetModule((ARCGIS_COM_GUID, 1, 0))


def _get_ao_module(module_name):
    """Import ArcGIS module"""
    from comtypes.client import GetModule
    sLibPath = _get_lib_path()
    GetModule(sLibPath + module_name)


def _get_lib_path():
    """Return location of ArcGIS type libraries as string"""
    # This will still work on 64-bit machines because Python runs in 32 bit mode
    import _winreg
    global ESRI_REGISTRY_PATH
    global ESRI_VERSION

    # Use cache
    if ESRI_REGISTRY_PATH is None:

        # Resolve ESRI installation directory by scanning the registry
        possiblePaths = ["SOFTWARE\\ESRI\\Desktop", "SOFTWARE\\Wow6432Node\\ESRI\\Desktop"]

        supportedVersions = [float("10.%d" % x) for x in reversed(range(3, 10))]

        for path in possiblePaths:
            for version in supportedVersions:
                candidate = "%s%s" % (path, version)
                if _registry_path_exists(candidate):
                    ESRI_REGISTRY_PATH = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, candidate)
                    ESRI_VERSION = version
                    break
            if ESRI_REGISTRY_PATH is not None:
                break

    if ESRI_REGISTRY_PATH == None:
        raise Exception("Could not resolve ESRI installation path from registry")

    return _winreg.QueryValueEx(ESRI_REGISTRY_PATH, "InstallDir")[0] + "com\\"


def _get_used_ao_modules():
    """Import commonly used ArcGIS libraries for standalone scripts"""
    _get_ao_module("esriCarto.olb")
    #_get_ao_module("esriDataSourcesGDB.olb")
    #_get_ao_module("esriDataSourcesFile.olb")
    #_get_ao_module("esriDisplay.olb")
    _get_ao_module("esriGeoDatabase.olb")
    #_get_ao_module("esriGeometry.olb")
    _get_ao_module("esriNetworkAnalyst.olb")
    #_get_ao_module("esriOutput.olb")
    _get_ao_module("esriSystem.olb")


def _init():
    import comtypes.gen.ArcGISVersionLib as esriVersion
    import comtypes.gen.esriSystem as esriSystem
    version_manager = create_obj(esriVersion.VersionManager, esriVersion.IArcGISVersion)
    if not version_manager.LoadVersion(esriVersion.esriArcGISDesktop, str(ESRI_VERSION)):
        raise RuntimeError("No ArcGIS Desktop version could be loaded.")

    init_context = create_obj(esriSystem.AoInitialize, esriSystem.IAoInitialize)

    # try standard product codes
    for product_code in (esriSystem.esriLicenseProductCodeAdvanced, esriSystem.esriLicenseProductCodeStandard,
                         esriSystem.esriLicenseProductCodeBasic):
        if init_context.IsProductCodeAvailable(product_code) != esriSystem.esriLicenseAvailable:
            continue

        if init_context.Initialize(product_code) == esriSystem.esriLicenseCheckedOut:
            return init_context

    raise RuntimeError("Could not initialize a licence.")


def _registry_path_exists(key):
    import _winreg
    try:
        _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, key)
        return True
    except:
        return False


def _shutdown_product(init_context):
    init_context.Shutdown()
    print("Shutdown")
    init_context = None


_bootstrap()