# Based on code from here: http://www.pierssen.com/arcgis10/python.htm

# Python 2/3 compatibility
from __future__ import (absolute_import, division, print_function, unicode_literals)
from future.builtins import *
from future.builtins.disabled import *
from future.standard_library import install_aliases
install_aliases()

# Pythonnet requires manual loading of dependencies where a dll references
# libraries in another folder
import sys
sys.path.append("C:\\Program Files\\ArcGIS\\Pro\\bin\\Extensions\Core")

import clr
# Dependencies of ArcGIS.Desktop.Core
clr.AddReference("ArcGIS.Desktop.Framework")
clr.AddReference("ArcGIS.Desktop.Shared.Wpf")
clr.AddReference("ArcGIS.Desktop.Ribbon.Wpf")
clr.AddReference("ArcGIS.Desktop.Docking.Wpf")
clr.AddReference("ArcGIS.Desktop.DataGrid.Contrib.Wpf")
clr.AddReference("ArcGIS.Desktop.Editors.Wpf")
clr.AddReference("ArcGIS.Core")
clr.AddReference("ESRI.ArcGIS.ItemIndex")

clr.AddReference("ArcGIS.Desktop.Core")

import asyncio

#**** Initialization ****
_esriVersion = 10.3
_esriRegistryPath = None

def GetEsriVersion():
    return _esriVersion

def RegistryPathExists(key):
    import _winreg
    try:
        _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, key)
        return True
    except:
        return False

def GetLibPath():
    """Return location of ArcGIS type libraries as string"""
    # This will still work on 64-bit machines because Python runs in 32 bit mode
    import _winreg
    global _esriRegistryPath
    global _esriVersion

    # Use cache
    if _esriRegistryPath is None:

        # Resolve ESRI installation directory by scanning the registry
        possiblePaths = [
            "SOFTWARE\\ESRI\\ArcGISPro"
            #"SOFTWARE\\Wow6432Node\\ESRI\\Desktop"
        ]

        supportedVersions = [float("10.%d" % x) for x in reversed(range(3, 10))]

        for path in possiblePaths:
            for version in supportedVersions:
                candidate = "%s%s" % (path, version)
                if RegistryPathExists(candidate):
                    _esriRegistryPath = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, candidate)
                    _esriVersion = version
                    break
            if _esriRegistryPath is not None:
                break

    if _esriRegistryPath == None:
        raise Exception("Could not resolve ESRI installation path from registry")

    return _winreg.QueryValueEx(_esriRegistryPath, "InstallDir")[0] + "com\\"

def GetModule(sModuleName):
    """Import ArcGIS module"""
    from comtypes.client import GetModule
    sLibPath = GetLibPath()
    GetModule(sLibPath + sModuleName)

def GetStandaloneModules():
    """Import commonly used ArcGIS libraries for standalone scripts"""
    GetModule("esriSystem.olb")
    GetModule("esriGeometry.olb")
    GetModule("esriCarto.olb")
    GetModule("esriDisplay.olb")
    GetModule("esriGeoDatabase.olb")
    GetModule("esriDataSourcesGDB.olb")
    GetModule("esriDataSourcesFile.olb")
    GetModule("esriOutput.olb")

def GetDesktopModules():
    """Import basic ArcGIS Desktop libraries"""
    GetModule("esriFramework.olb")
    GetModule("esriArcMapUI.olb")
    GetModule("esriArcCatalogUI.olb")

#**** Helper Functions ****

def NewObj(MyClass, MyInterface):
    """Creates a new comtypes POINTER object where\n\
    MyClass is the class to be instantiated,\n\
    MyInterface is the interface to be assigned"""
    from comtypes.client import CreateObject
    try:
        ptr = CreateObject(MyClass, interface=MyInterface)
        return ptr
    except:
        return None

def CType(obj, interface):
    """Casts obj to interface and returns comtypes POINTER or None"""
    try:
        newobj = obj.QueryInterface(interface)
        return newobj
    except:
        return None

def CLSID(MyClass):
    """Return CLSID of MyClass as string"""
    return str(MyClass._reg_clsid_)


# Instance reference
pInit = None

def InitStandalone():
    global pInit
    """Init standalone ArcGIS license"""
    # Set ArcObjects version
    import comtypes
    from comtypes.client import GetModule
    g = comtypes.GUID("{6FCCEDE0-179D-4D12-B586-58C88D26CA78}")
    GetModule((g, 1, 0))
    import comtypes.gen.ArcGISVersionLib as esriVersion
    import comtypes.gen.esriSystem as esriSystem
    pVM = NewObj(esriVersion.VersionManager, esriVersion.IArcGISVersion)
    if not pVM.LoadVersion(esriVersion.esriArcGISDesktop, str(_esriVersion)):
        return False
    # Get license
    pInit = NewObj(esriSystem.AoInitialize, esriSystem.IAoInitialize)
    ProductList = [esriSystem.esriLicenseProductCodeAdvanced, \
                   esriSystem.esriLicenseProductCodeStandard, \
                   esriSystem.esriLicenseProductCodeBasic]
    for eProduct in ProductList:
        licenseStatus = pInit.IsProductCodeAvailable(eProduct)
        if licenseStatus != esriSystem.esriLicenseAvailable:
            continue
        licenseStatus = pInit.Initialize(eProduct)
        return (licenseStatus == esriSystem.esriLicenseCheckedOut)
    return False


def ShutdownStandalone():
    global pInit
    pInit.Shutdown()
    pInit = None

def init_arcobjects_context():
    GetStandaloneModules()
    InitStandalone()

def destroy_arcobjects_context():
    ShutdownStandalone()

def project_exists(mxd_path):
    clr.AddReference("ArcGIS.Desktop.Core")
    from ArcGIS.Desktop.Core import Project

    ArcProVersion = ""
    result = Project.CanOpen(mxd_path, ArcProVersion)
    return result

def create_project(project_path):
    from ArcGIS.Desktop.Core import Project, CreateProjectSettings

    settings = CreateProjectSettings()
    settings.set_LocationPath(project_path)

    try:
        project = Project.CreateAsync(settings)
        return project.Result
    except Exception as e:
        raise e

def open_project(mxd_path):
    from ArcGIS.Desktop.Core import Project

    try:
        task = Project.OpenAsync(mxd_path)
        if task.get_IsCompleted():
            return Project.OpenAsync(mxd_path).Result
    except Exception as e:
        raise e

    """if Project.CanOpen(mxd_path, ArcProVersion)[0]:
        return Project.OpenAsync(mxd_path)
    else:
        raise Exception("Project can not be opened")"""

def list_layers(project_uri):

    """import comtypes.gen.esriSystem as esriSystem
    import comtypes.gen.esriGeoDatabase as esriGeoDatabase
    import comtypes.gen.esriCarto as esriCarto"""

    # Open project
    project = open_project(project_uri)

    res = {}

    # Use MxdServer for reading map layer descriptions
    """mxdServer = NewObj(esriCarto.MxdServer, esriCarto.IMxdServer)
    mxdServer.Start(mxd_path)"""

    # Enumerate maps
    for i in range(0, len(project.ListMaps())):

        pMap = CType(mapDoc.Map(i), esriCarto.IMap)

        # Enumerate layer descriptions
        descriptors = CType(mxdServer.LayerDescriptors(pMap.Name), esriSystem.IArray)
        for d in range(0, descriptors.Count):
            desc = CType(descriptors.Element(d), esriCarto.ILayerDescriptor)
            name = desc.Name

            res[name] = {
                'name': name
            }

            res[name]['id'] = desc.ID
            res[name]['hasFixedId'] = False
            res[name]['visible'] = desc.Visible
            res[name]['definitionQuery'] = desc.DefinitionExpression

    # Override layers Ids with fixed layer Ids (if set)
    try:

        # Dataframes
        for mapIndex in range(0, mapDoc.MapCount):
            map = CType(mapDoc.Map(mapIndex), esriCarto.IMap)

            # Layers
            for layerIndex in range(0, map.LayerCount):

                layer = CType(map.Layer(layerIndex), esriCarto.ILayer)
                layerExt = CType(map.Layer(layerIndex), esriCarto.ILayerExtensions)

                # Extensions
                for extIndex in range(0, layerExt.ExtensionCount):
                    ext = CType(layerExt.Extension(extIndex), esriCarto.IServerLayerExtension)

                    # Extension properties
                    props = CType(ext.ServerProperties, esriSystem.IPropertySet)
                    propSet = props.GetAllProperties()

                    names = propSet[0]
                    values = propSet[1]

                    for nameIndex in range(0, len(names)):
                        if names[nameIndex] == "ServiceLayerID":
                            fixedLayerId = values[nameIndex]
                            if res[layer.Name]['id'] != fixedLayerId:
                                res[layer.Name]['id'] = fixedLayerId
                                res[layer.Name]['hasFixedId'] = True

    except Exception as e:
        print("Could not resolve fixed layer IDs", e)

    mapDoc.Close()

    return res

