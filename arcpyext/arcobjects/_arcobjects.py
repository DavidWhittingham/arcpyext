# Based on code from here: http://www.pierssen.com/arcgis10/python.htm

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
            "SOFTWARE\\ESRI\\Desktop",
            "SOFTWARE\\Wow6432Node\\ESRI\\Desktop"
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

def mxd_exists(mxd_path):
    import comtypes.gen.esriCarto as esriCarto
    pMapDoc = NewObj(esriCarto.MapDocument, esriCarto.IMapDocument)
    exists = pMapDoc.IsPresent(mxd_path)
    valid = pMapDoc.IsMapDocument(mxd_path)
    return exists and valid

def open_mxd(mxd_path):
    import comtypes.gen.esriSystem as esriSystem
    import comtypes.gen.esriGeoDatabase as esriGeoDatabase
    import comtypes.gen.esriCarto as esriCarto

    mapDoc = NewObj(esriCarto.MapDocument, esriCarto.IMapDocument)

    if mxd_exists(mxd_path):
        mapDoc.Open(mxd_path)
        return mapDoc
    else:
        raise Exception("Mxd not found or invalid")

def list_layers(mxd_path):

    import comtypes.gen.esriSystem as esriSystem
    import comtypes.gen.esriGeoDatabase as esriGeoDatabase
    import comtypes.gen.esriCarto as esriCarto

    # Open MXD
    mapDoc = open_mxd(mxd_path)

    res = {}

    # Use MxdServer for reading map layer descriptions
    mxdServer = NewObj(esriCarto.MxdServer, esriCarto.IMxdServer)
    mxdServer.Start(mxd_path)

    # Enumerate maps
    for i in range(0, mapDoc.MapCount):

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
                            if res[layer.Name]['id'] <> fixedLayerId:
                                res[layer.Name]['id'] = fixedLayerId
                                res[layer.Name]['hasFixedId'] = True

    except Exception as e:
        print("Could not resolve fixed layer IDs", e)

    mapDoc.Close()

    return res