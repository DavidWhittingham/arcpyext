import xml.etree.ElementTree as ET
import xml.dom.minidom as DOM

class SDDraft(object):
    """description of class"""

    ANTI_ALIASING_MODES = type("Enum", (), dict(NONE="None", FASTEST="Fastest", FAST="Fast", NORMAL="Normal", 
        BEST="Best"))
    EXTENSIONS = type("Enum", (), dict(FEATURESERVER='FeatureServer', MOBILESERVER='MobileServer', 
        WMSSERVER='WMSServer', KMLSERVER='KmlServer', NASERVER='NAServer', WFSSERVER='WFSServer', 
        WCSSERVER='WCSServer', SCHEMATICSSERVER='SchematicsServer'))
    TEXT_ANTI_ALIASING_MODES = type("Enum", (), dict(NONE = "None", FORCE = "Force", NORMAL = "Normal"))

    def __init__(self, path):
        self._path = path
        self._xmltree = self._parse_xmlns(path)

    #####################
    # PUBLIC PROPERTIES #
    #####################

    @property
    def anti_aliasing_mode(self):
        aa = self._get_anti_aliasing_element()
        return self._get_element_value(aa)

    @anti_aliasing_mode.setter
    def anti_aliasing_mode(self, value):
        aa = self._get_anti_aliasing_element()
        self._set_element_value(aa, value)
        
    
    @property
    def cluster(self):
        return self._get_element_value(self._get_first_element_by_tag("Cluster"))

    @cluster.setter
    def cluster(self, value):
        self._set_element_value(self._get_first_element_by_tag("Cluster"), value)

        
    @property
    def description(self):
        description_props = self._get_description_elements()
        return self._get_element_value(description_props[0])

    @description.setter
    def description(self, value):
        for prop in self._get_description_elements():
            self._set_element_value(prop, value)
    
    
    @property
    def enabled_extensions(self):
        """Gets a list of the extensions (by type name) that are currently enabled for the service."""
        return self._get_extension_names()

    @enabled_extensions.setter
    def enabled_extensions(self, values):
        """Sets the extensions (by an iterable of type names) that are enabled for the service. Valid extension type 
        names are 'FeatureServer', 'MobileServer', 'WMSServer', 'KmlServer', 'NAServer', 'WFSServer', 'WCSServer' and 
        'SchematicsServer'.  Custom extensions will also (theoretically) work, as long as there configuration already 
        exists in the SD Draft."""
        self._set_enabled_extensions_by_types(values)


    @property
    def file_path(self):
        return self._path
    
    
    @property
    def high_isolation(self):
        """Gets a boolean value that describes if the service is set to high isolation (true) or low isolation 
        (false)."""
        isolation = self._get_element_value(self._get_isolation_element())
        return True if isolation.upper() == "HIGH" else False

    @high_isolation.setter
    def high_isolation(self, value):
        """Sets a boolean value that describes if the service is set to high isolation (true) or low isolation 
        (false)."""
        self._set_element_value(self._get_isolation_element(), 
            "HIGH" if value == True else "LOW")

    
    @property
    def instances_per_container(self):
        return self._get_element_value(self._get_instances_per_container_element())

    @instances_per_container.setter
    def instances_per_container(self, value):
        self._set_element_value(self._get_instances_per_container_element(), value)


    @property
    def keep_cache(self):
        """Gets a boolean value that describes if the service should keep its cache on publish."""
        keep_cache_value = self._get_element_value(self._get_first_element_by_tag("KeepExistingMapCache"))
        return True if keep_cache_value.upper() == "TRUE" else False

    @keep_cache.setter
    def keep_cache(self, value):
        """Sets a boolean value that describes if the service should keep its cache on publish."""
        try:
            value = value.upper()
            value = True if value in ["TRUE", "T"] else False
        except AttributeError:
            pass
            
        self._set_element_value(self._get_first_element_by_tag("KeepExistingMapCache"), 
            "true" if value == True else "false")
    
    
    @property
    def min_instances(self):
        return self._get_element_value(self._get_min_instances_element())

    @min_instances.setter
    def min_instances(self, value):
        if value < 0:
            raise ValueError("Min instances cannot be less than zero.")
        self._set_element_value(self._get_min_instances_element(), value)


    @property
    def max_instances(self):
        return self._get_element_value(self._get_max_instances_element())

    @max_instances.setter
    def max_instances(self, value):
        if value < self.min_instances or value <= 0:
            raise ValueError("Max instances cannot be 0 or less than the minimum instances.")
        self._set_element_value(self._get_max_instances_element(), value)
            

    @property
    def name(self):
        name_props = self._get_name_elements()
        return self._get_element_value(name_props[0])

    @name.setter
    def name(self, value):
        if value == "":
            raise ValueError("Name string cannot be empty")
        for prop in self._get_name_elements():
            self._set_element_value(prop, value)


    @property
    def replace_existing(self):
       manifest_type = self._get_first_element_by_tag("Type")
       return False \
           if self._get_element_value(self._get_first_element_by_tag("Type")) == "esriServiceDefinitionType_New" \
           else True

    @replace_existing.setter
    def replace_existing(self, value):
        manifest_type = self._get_first_element_by_tag("Type")
        self._set_element_value(manifest_type, 
                        "esriServiceDefinitionType_Replacement" if value == True else "esriServiceDefinitionType_New")


    @property
    def summary(self):
        summary_props = self._get_summary_elements()
        return self._get_element_value(summary_props[0])

    @summary.setter
    def summary(self, value):
        for prop in self._get_summary_elements():
            self._set_element_value(prop, value)


    @property
    def text_anti_aliasing_mode(self):
        aa = self._get_text_anti_aliasing_element()
        return self._get_element_value(aa)

    @text_anti_aliasing_mode.setter
    def text_anti_aliasing_mode(self, value):
        aa = self._get_text_anti_aliasing_element()
        self._set_element_value(aa, value)


    @property
    def wait_timeout(self):
        return self._get_element_value(self._get_wait_timeout_element())

    @wait_timeout.setter
    def wait_timeout(self, value):
        self._set_element_value(self._get_wait_timeout_element(), value)


    ##################
    # PUBLIC METHODS #
    ##################

    def save(self):
        self.save_a_copy(self._path)

    def save_a_copy(self, path):
        #self._xmltree.write(path)
        # ElementTree doesn't escape double quotes in element values where as the original SD Draft file from Esri does
        # Using Minidom because it escapes double quotes, just to be sure we're compatible

        f = open(path, 'w')
        xml_string = ET.tostring(self._xmltree.getroot())
        xml = DOM.parseString(xml_string)
        xml.writexml(f)
        f.close()

    ###################
    # PRIVATE METHODS #
    ###################

    # SDDraft XML Helpers
    def _get_anti_aliasing_element(self):
        serv_props = self._get_service_configuration_properties()
        return [item.find("Value") for item in list(serv_props) if item.findtext("Key") == "antialiasingMode"][0]

    def _get_description_elements(self):
        item_info = self._get_first_element_by_tag("ItemInfo")
        return [item_info.find("Description")]

    def _get_extension_names(self):
        exts = self._get_elements_by_tag("SVCExtension")
        return [self._get_element_value(item.find("TypeName")) for item in exts if self._get_element_value(item.find("Enabled")).lower() == "true"]

    def _get_instances_per_container_element(self):
        return self._get_value_element_by_key(self._get_service_props(), "InstancesPerContainer")

    def _get_isolation_element(self):
        return self._get_value_element_by_key(self._get_service_props(), "Isolation")

    def _get_min_instances_element(self):
        return self._get_value_element_by_key(self._get_service_props(), "MinInstances")

    def _get_max_instances_element(self):
        return self._get_value_element_by_key(self._get_service_props(), "MaxInstances")

    def _get_name_elements(self):
        sm_name = self._get_first_element_by_tag("SVCManifest").find("Name")        
        sc_name = self._get_first_element_by_tag("SVCConfiguration").find("Name")

        wcs_ext_props = self._get_service_extension_by_type("WCSServer").find("./Props/PropertyArray").findall("PropertySetProperty")
        wcs_ext_name_props = self._get_value_elements_by_keys(wcs_ext_props, ["name"])

        wfs_ext_props = self._get_service_extension_by_type("WFSServer").find("./Props/PropertyArray").findall("PropertySetProperty")
        wfs_ext_name_props = self._get_value_elements_by_keys(wfs_ext_props, ["name", "appSchemaPrefix"])

        return [sm_name, sc_name] + wcs_ext_name_props + wfs_ext_name_props

    def _get_service_configuration_properties(self):
        return list(self._xmltree.getroot().find("./Configurations/SVCConfiguration/Definition/ConfigurationProperties/PropertyArray"))

    def _get_service_extension_by_type(self, type_name):
        extensions = [item for item in self._get_elements_by_tag("SVCExtension") if item.findtext("TypeName") == type_name]
        return extensions[0] if len(extensions) == 1 else None

    def _get_service_props(self):
        return list(self._xmltree.getroot().find("./Configurations/SVCConfiguration/Definition/Props/PropertyArray"))

    def _get_summary_elements(self):
        item_info = self._get_first_element_by_tag("ItemInfo")
        return [item_info.find("Snippet")]

    def _get_text_anti_aliasing_element(self):
        return self._get_value_element_by_key(self._get_service_configuration_properties(), "textAntialiasingMode")

    def _get_value_element_by_key(self, prop_list, key):
        """ From a list of PropertySetProperty elements, return the "value" child element of the first 
        PropertySetProperty element with a particular key."""
        return next(item.find("Value") for item in list(prop_list) if item.findtext("Key") == key)

    def _get_value_elements_by_keys(self, prop_list, keys):
        """ From a list of PropertySetProperty elements, returns a list of the "value" child elements of 
        PropertySetProperty elements with a particular key."""
        return [item.find("Value") for item in list(prop_list) if item.findtext("Key") in keys]

    def _get_wait_timeout_element(self):
        return self._get_value_element_by_key(self._get_service_props(), "WaitTimeout")

    def _set_enabled_extensions_by_types(self, types):
        types = [t.lower() for t in types]
        for ext in self._get_elements_by_tag("SVCExtension"):
            type = self._get_element_value(ext.find("TypeName"))
            if type.lower() in types:
                self._set_element_value(ext.find("Enabled"), "true")
            else:
                self._set_element_value(ext.find("Enabled"), "false")


    # Generic XML Helpers
    def _get_element_value(self, element):
        return element.text

    def _get_elements_by_tag(self, tag_name):
        return list(self._xmltree.getroot().iter(tag_name))

    def _get_first_element_by_tag(self, tag_name):
        return next(self._xmltree.getroot().iter(tag_name))

    def _parse_xmlns(self, file):
        """Parses an XML file whilst preserving custom namespaces, which ElementTree doesn't do out of the box"""

        root = None
        ns_map = []

        for event, elem in ET.iterparse(file, ("start", "start-ns")):

            if event == "start-ns" and elem[0] != "xsi":
                # xsi is the only namespace supported out of the box, we don't need it twice so it is ignored
                ns_map.append(elem)

            elif event == "start":
                if root is None:
                    root = elem
                for prefix, uri in ns_map:
                    elem.set("xmlns:" + prefix, uri)
                ns_map = []

        return ET.ElementTree(root)

    def _set_element_value(self, element, value):
        element.text = value