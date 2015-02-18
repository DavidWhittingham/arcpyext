import codecs
import datetime
import re
import xml.etree.ElementTree as ET
import xml.dom.minidom as DOM

class SDDraft(object):
    """Class for editing a Service Definition Draft.

    Must be instantiated from an on-disk SDDraft file generated."""

    ANTI_ALIASING_MODES = type("Enum", (), dict(NONE="None", FASTEST="Fastest", FAST="Fast", NORMAL="Normal",
        BEST="Best"))
    EXTENSIONS = type("Enum", (), dict(FEATURESERVER='FeatureServer', MOBILESERVER='MobileServer',
        WMSSERVER='WMSServer', KMLSERVER='KmlServer', NASERVER='NAServer', WFSSERVER='WFSServer',
        WCSSERVER='WCSServer', SCHEMATICSSERVER='SchematicsServer'))
    FEATURE_ACCESS_OPERATIONS = type("Enum", (), dict(CREATE='Create', QUERY='Query', UPDATE='Update',
        DELETE='Delete', SYNC='Sync'))
    TEXT_ANTI_ALIASING_MODES = type("Enum", (), dict(NONE = "None", FORCE = "Force", NORMAL = "Normal"))

    _TIME_STRING_REGEX = re.compile(r"^([0-9]{2}):([0-9]{2})$")
    _FEATURE_ACCESS_EDIT_OPERATIONS = ["Create", "Delete", "Update"]

    def __init__(self, path):
        self._path = path
        self._xmltree = self._parse_xmlns(path)

    #####################
    # PUBLIC PROPERTIES #
    #####################

    @property
    def anti_aliasing_mode(self):
        """Gets the current anti-aliasing mode for map graphics."""
        return self._get_element_value(self._get_anti_aliasing_element())

    @anti_aliasing_mode.setter
    def anti_aliasing_mode(self, value):
        """Sets the anti-aliasing mode for map graphics.

        Valid values are contained in the 'arcpyext.mapping.SDDraft.ANTI_ALIASING_MODES' enumerated type.
        """
        self._set_element_value(self._get_anti_aliasing_element(), value)


    @property
    def cluster(self):
        """Gets a list of cluster names that the published service will run on."""
        clusters = self._get_element_value(self._get_first_element_by_tag("Cluster"))
        return clusters.split(",")

    @cluster.setter
    def cluster(self, value):
        """Sets a list of cluster names that the published service will run on.

        Accepts either a string (including a comma-separated string list), or any string-based sequence.
        """
        if isinstance(value, basestring):
            value = [val.strip() for val in value.split(",")]

        self._set_element_value(self._get_first_element_by_tag("Cluster"), ",".join(value))


    @property
    def description(self):
        """Gets the description for the service."""
        return self._get_element_value(self._get_description_element())

    @description.setter
    def description(self, value):
        """Sets the description for the service."""
        self._set_element_value(self._get_description_element(), value)


    @property
    def disable_identify_relates(self):
        """Gets a boolean indicating whether or not displaying related information in identify results is enabled."""
        return self._value_to_boolean(
            self._get_element_value(
                self._get_disable_identify_relates_element()))

    @disable_identify_relates.setter
    def disable_identify_relates(self, value):
        value = self._value_to_boolean(value)
        self._set_element_value(
            self._get_disable_identify_relates_element(),
            self._boolean_to_text(value))


    @property
    def enable_dynamic_layers(self):
        """Gets a boolean value indicating whether or not dynamic layer order and symbology are enabled."""
        return self._value_to_boolean(
            self._get_element_value(
                self._get_enable_dynamic_layers_element()))

    @enable_dynamic_layers.setter
    def enable_dynamic_layers(self, value):
        """Gets a boolean value indicating whether or not dynamic layer order and symbology are enabled."""
        value = self._value_to_boolean(value)
        self._set_element_value(
            self._get_enable_dynamic_layers_element(),
            self._boolean_to_text(value))


    @property
    def enabled_extensions(self):
        """Gets a list of the extensions (by type name) that are currently enabled for the service."""
        return self._get_extension_names()

    @enabled_extensions.setter
    def enabled_extensions(self, values):
        """Sets the extensions (by an iterable of type names) that are enabled for the service.

        Valid values are contained in the 'arcpyext.mapping.SDDraft.EXTENSIONS' enumerated type.
        Valid string values are:
         - 'FeatureServer'
         - 'MobileServer'
         - 'WMSServer'
         - 'KmlServer'
         - 'NAServer'
         - 'WFSServer'
         - 'WCSServer'
         - 'SchematicsServer'

        Custom extensions will also (theoretically) work, as long as there configuration already
        exists in the Service Definition Draft.
        """
        self._set_enabled_extensions_by_types(values)


    @property
    def feature_access_enabled_operations(self):
        """Gets a list of the enabled operations (by type name) that are currently enabled for the feature service."""
        values = self._get_enabled_feature_operations()
        # remove "Uploads" and "Editing" as these are internal operations not exposed in the ArcMap/Server UI.
        return [val for val in values if val not in {"Uploads","Editing"}]

    @feature_access_enabled_operations.setter
    def feature_access_enabled_operations(self, values):
        """Sets the operations (by an iterable of operation names) that are enabled for the feature service.

        Valid values are contained in the 'arcpyext.mapping.SDDraft.FEATURE_ACCESS_OPERATIONS' enumerated type.
        Valid string values are:
         - 'Create'
         - 'Query'
         - 'Update'
         - 'Delete'
         - 'Sync'
        """
        #Convert all operation names to title case because that is what ArcMap outputs
        values = set([val.title() for val in values])
        if [val for val in values if val not in (
            self.FEATURE_ACCESS_OPERATIONS.CREATE,
            self.FEATURE_ACCESS_OPERATIONS.QUERY,
            self.FEATURE_ACCESS_OPERATIONS.UPDATE,
            self.FEATURE_ACCESS_OPERATIONS.DELETE,
            self.FEATURE_ACCESS_OPERATIONS.SYNC
            )]:
            # not a known operation, raise exception
            raise ValueError("Operations list contains invalid operation types.")

        if [val for val in values if val in self._FEATURE_ACCESS_EDIT_OPERATIONS]:
            # if operation is in the _FEATURE_ACCESS_EDIT_OPERATIONS list, the "Uploads" and "Editing" operations
            # must also be enabled.  This functionality is hidden the UI, but occurs when creating the draft in ArcMap
            values.update({"Uploads","Editing"})
        self._set_enabled_feature_operations(values)


    @property
    def file_path(self):
        """Gets the file path to the Service Definition Draft."""
        return self._path
        
    
    @property
    def folder(self):
        """Gets the name of the folder that the service will reside in."""
        return self._get_element_value(self._get_folder_element())
    
    @folder.setter
    def folder(self, value):
        """Sets the name of the folder that the service will reside in."""
        value = "" if value == None else value
        self._set_element_value(self._get_folder_element(), value)
        self._set_full_path_properties()


    @property
    def high_isolation(self):
        """Gets a boolean that describes if the service is set to high isolation (true) or low isolation (false)."""
        isolation = self._get_element_value(self._get_isolation_element())
        return True if isolation.upper() == "HIGH" else False

    @high_isolation.setter
    def high_isolation(self, value):
        """Sets a boolean that describes if the service is set to high isolation (true) or low isolation (false)."""
        self._set_element_value(self._get_isolation_element(),
            "HIGH" if value == True else "LOW")


    @property
    def idle_timeout(self):
        """Gets the idle timeout (in seconds) for the service."""
        return int(self._get_element_value(self._get_idle_timeout_element()))

    @idle_timeout.setter
    def idle_timeout(self, value):
        """Sets the idle timeout (in seconds) for the service."""
        if value < 0:
            raise ValueError("Timeout cannot be less than zero.")
        self._set_element_value(self._get_idle_timeout_element(), value)


    @property
    def instances_per_container(self):
        """Gets the number of instances of this service can run per container (i.e. process).

        Only applicable when running in low isolation.
        """
        return int(self._get_element_value(self._get_instances_per_container_element()))

    @instances_per_container.setter
    def instances_per_container(self, value):
        """Sets the number of instances of this service can run per container (i.e. process).

        Only applicable when running in low isolation.
        """
        self._set_element_value(self._get_instances_per_container_element(), value)


    @property
    def keep_cache(self):
        """Gets a boolean value that describes if the service should keep its cache on publish."""
        return self._value_to_boolean(self._get_element_value(self._get_first_element_by_tag("KeepExistingMapCache")))

    @keep_cache.setter
    def keep_cache(self, value):
        """Sets a boolean value that describes if the service should keep its cache on publish."""
        value = self._value_to_boolean(value)

        self._set_element_value(self._get_first_element_by_tag("KeepExistingMapCache"),
            self._boolean_to_text(value))


    @property
    def max_instances(self):
        """Gets the maximum number of instances that the published service will run."""
        return int(self._get_element_value(self._get_max_instances_element()))

    @max_instances.setter
    def max_instances(self, value):
        """Sets the maximum number of instances that the published service will run."""
        if value < self.min_instances or value <= 0:
            raise ValueError("Max instances cannot be 0 or less than the minimum instances.")
        self._set_element_value(self._get_max_instances_element(), value)


    @property
    def max_record_count(self):
        """Gets the maximum number of records that can be returned by the service."""
        return int(self._get_element_value(self._get_max_record_count_element()))

    @max_record_count.setter
    def max_record_count(self, value):
        """Sets the maximum number of records that can be returned by the service."""
        if value < 0:
            raise ValueError("Maximum record count cannot be less than zero.")
        self._set_element_value(self._get_max_record_count_element(), value)


    @property
    def min_instances(self):
        """Gets the minimum number of instances that the published service will run."""
        return int(self._get_element_value(self._get_min_instances_element()))

    @min_instances.setter
    def min_instances(self, value):
        """Sets the minimum number of instances that the published service will run."""
        if value < 0:
            raise ValueError("Min instances cannot be less than zero.")
        self._set_element_value(self._get_min_instances_element(), value)


    @property
    def name(self):
        """Gets the name of the service."""
        name_props = self._get_name_elements()
        return self._get_element_value(name_props[0])

    @name.setter
    def name(self, value):
        """Sets the name of the service (Cannot be an empty value)."""
        if value == "":
            raise ValueError("Name string cannot be empty")
        for prop in self._get_name_elements():
            self._set_element_value(prop, value)
            
        self._set_full_path_properties()

    @property
    def recycle_interval(self):
        """Gets the recycle interval (in hours)."""
        return int(self._get_element_value(self._get_recycle_interval_element()))

    @recycle_interval.setter
    def recycle_interval(self, value):
        """Sets the recycle interval (in hours)."""
        if value < 0:
            raise ValueError("Recycle interval must not be less than zero.")
        self._set_element_value(self._get_recycle_interval_element(), value)


    @property
    def recycle_start_time(self):
        """Gets the recycle time for the service.

        Returns:
         - Recycle time for the service as a 'datetime.time' object
        """
        time = self._get_element_value(self._get_recycle_start_time_element())
        if time == None or time == "":
            return datetime.time(0,0)
        else:
            time_parts = time.split(":")
            return datetime.time(int(time_parts[0]), int(time_parts[1]))

    @recycle_start_time.setter
    def recycle_start_time(self, value):
        """Sets the recycle time for the service.

        Arguments:
        value -- The recycle time.  Can be a string in format "hh:mm" or a datetime.time object.
        """
        if isinstance(value, basestring):
            if self._TIME_STRING_REGEX.match(value) != None:
                self._set_element_value(self._get_recycle_start_time_element(), value)
            else:
                raise ValueError("Time string in incorrect format, must be in format 'hh:mm'.")
        else:
            value = "{0}:{1}".format(value.hour, value.minute)
            self._set_element_value(self._get_recycle_start_time_element(), value)

    @property
    def replace_existing(self):
        """Gets a boolean indicating whether or not a service of the same name will be replaced on publish."""
        manifest_type = self._get_first_element_by_tag("Type")
        if self._get_element_value(self._get_first_element_by_tag("Type")) == "esriServiceDefinitionType_New":
            return False
        else:
            return True

    @replace_existing.setter
    def replace_existing(self, value):
        """Sets a boolean indicating whether or not a service of the same name will be replaced on publish."""
        value = self._value_to_boolean(value)
        manifest_type = self._get_first_element_by_tag("Type")
        self._set_element_value(
            manifest_type,
            "esriServiceDefinitionType_Replacement" if value == True else "esriServiceDefinitionType_New")


    @property
    def schema_locking_enabled(self):
        """Gets a boolean indicating whether or not the server locks the database schema."""
        return self._value_to_boolean(self._get_element_value(self._get_schema_locking_enabled_element()))

    @schema_locking_enabled.setter
    def schema_locking_enabled(self, value):
        """Sets a boolean indicating whether or not the server locks the database schema."""
        value = self._value_to_boolean(value)
        self._set_element_value(self._get_schema_locking_enabled_element(), self._boolean_to_text(value))


    @property
    def summary(self):
        """Gets the summary for the service."""
        return self._get_element_value(self._get_summary_element())

    @summary.setter
    def summary(self, value):
        """Sets the summary for the service."""
        self._set_element_value(self._get_summary_element(), value)


    @property
    def text_anti_aliasing_mode(self):
        """Gets the current anti-aliasing mode for map text."""
        aa = self._get_text_anti_aliasing_element()
        return self._get_element_value(aa)

    @text_anti_aliasing_mode.setter
    def text_anti_aliasing_mode(self, value):
        """Sets the anti-aliasing mode for map graphics.

        Valid values are contained in the 'arcpyext.mapping.SDDraft.TEXT_ANTI_ALIASING_MODES' enumerated type.
        """
        aa = self._get_text_anti_aliasing_element()
        self._set_element_value(aa, value)


    @property
    def usage_timeout(self):
        """Gets the usage timeout (in seconds) for the service."""
        return int(self._get_element_value(self._get_usage_timeout_element()))

    @usage_timeout.setter
    def usage_timeout(self, value):
        """Sets the usage timeout (in seconds) for the service."""
        if value < 0:
            raise ValueError("Timeout cannot be less than zero.")
        self._set_element_value(self._get_usage_timeout_element(), value)


    @property
    def wait_timeout(self):
        """Gets the wait timeout (in seconds) for the service."""
        return int(self._get_element_value(self._get_wait_timeout_element()))

    @wait_timeout.setter
    def wait_timeout(self, value):
        """Sets the wait timeout (in seconds) for the service."""
        if value < 0:
            raise ValueError("Timeout cannot be less than zero.")
        self._set_element_value(self._get_wait_timeout_element(), value)


    ##################
    # PUBLIC METHODS #
    ##################

    def save(self):
        """Saves changes to the Service Definition Draft back to the file."""
        self.save_a_copy(self._path)

    def save_a_copy(self, path):
        """Saves a copy of the Service Definition Draft to a new file."""
        #self._xmltree.write(path)
        # ElementTree doesn't escape double quotes in element values where as the original SD Draft file from Esri does
        # Using Minidom because it escapes double quotes, just to be sure we're compatible

        f = codecs.open(path, 'w', "utf-8")
        xml_string = ET.tostring(self._xmltree.getroot())
        xml = DOM.parseString(xml_string.encode("utf-8"))
        xml.writexml(f, encoding = "utf-8")
        f.close()

    ###################
    # PRIVATE METHODS #
    ###################

    def _boolean_to_text(self, value):
        return "true" if value == True else "false"

    def _value_to_boolean(self, value):
        """Converts true-ish and false-ish values to boolean."""
        try:
            value = value.upper()
            value = True if value in ["TRUE", "T"] else False
        except AttributeError:
            pass

        return value == True

    # SDDraft XML Helpers
    def _get_anti_aliasing_element(self):
        return self._get_value_element_by_key(self._get_service_configuration_properties(), "antialiasingMode")

    def _get_description_element(self):
        item_info = self._get_first_element_by_tag("ItemInfo")
        return item_info.find("Description")

    def _get_disable_identify_relates_element(self):
        return self._get_value_element_by_key(
            self._get_service_configuration_properties(),
            "disableIdentifyRelates")

    def _get_enable_dynamic_layers_element(self):
        return self._get_value_element_by_key(
            self._get_service_configuration_properties(),
            "enableDynamicLayers")

    def _get_enabled_feature_operations(self):
        ext_props = self._get_service_extension_by_type("FeatureServer").find("./Info/PropertyArray")
        enabled_ops_prop = self._get_value_element_by_key(ext_props, "WebCapabilities")
        return self._get_element_value(enabled_ops_prop).split(",")

    def _get_extension_names(self):
        exts = self._get_elements_by_tag("SVCExtension")
        return [self._get_element_value(item.find("TypeName")) for item in exts if self._get_element_value(item.find("Enabled")).lower() == "true"]
        
    def _get_folder_element(self):
        return self._get_first_element_by_tag("SVCConfiguration").find("ServiceFolder")

    def _get_idle_timeout_element(self):
        return self._get_value_element_by_key(self._get_service_props(), "IdleTimeout")

    def _get_instances_per_container_element(self):
        return self._get_value_element_by_key(self._get_service_props(), "InstancesPerContainer")

    def _get_isolation_element(self):
        return self._get_value_element_by_key(self._get_service_props(), "Isolation")

    def _get_max_instances_element(self):
        return self._get_value_element_by_key(self._get_service_props(), "MaxInstances")

    def _get_max_record_count_element(self):
        return self._get_value_element_by_key(self._get_service_configuration_properties(), "maxRecordCount")

    def _get_min_instances_element(self):
        return self._get_value_element_by_key(self._get_service_props(), "MinInstances")

    def _get_name_elements(self):
        sm_name = self._get_first_element_by_tag("SVCManifest").find("Name")
        sc_name = self._get_first_element_by_tag("SVCConfiguration").find("Name")

        wcs_ext_props = self._get_service_extension_by_type("WCSServer").find("./Props/PropertyArray").findall("PropertySetProperty")
        wcs_ext_name_props = self._get_value_elements_by_keys(wcs_ext_props, ["name"])
        
        wfs_ext_props = self._get_service_extension_by_type("WFSServer").find("./Props/PropertyArray").findall("PropertySetProperty")
        wfs_ext_name_props = self._get_value_elements_by_keys(wfs_ext_props, ["name"])

        return [sm_name, sc_name] + wcs_ext_name_props + wfs_ext_name_props

    def _get_recycle_start_time_element(self):
        return self._get_value_element_by_key(self._get_service_props(), "recycleStartTime")

    def _get_recycle_interval_element(self):
        return self._get_value_element_by_key(self._get_service_props(), "recycleInterval")

    def _get_service_configuration_properties(self):
        return list(self._xmltree.getroot().find("./Configurations/SVCConfiguration/Definition/ConfigurationProperties/PropertyArray"))

    def _get_schema_locking_enabled_element(self):
        return self._get_value_element_by_key(self._get_service_configuration_properties(), "schemaLockingEnabled")

    def _get_service_extension_by_type(self, type_name):
        extensions = [item for item in self._get_elements_by_tag("SVCExtension") if item.findtext("TypeName") == type_name]
        return extensions[0] if len(extensions) == 1 else None

    def _get_service_props(self):
        return list(self._xmltree.getroot().find("./Configurations/SVCConfiguration/Definition/Props/PropertyArray"))

    def _get_summary_element(self):
        item_info = self._get_first_element_by_tag("ItemInfo")
        return item_info.find("Snippet")

    def _get_text_anti_aliasing_element(self):
        return self._get_value_element_by_key(self._get_service_configuration_properties(), "textAntialiasingMode")

    def _get_usage_timeout_element(self):
        return self._get_value_element_by_key(self._get_service_props(), "UsageTimeout")

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

    def _set_enabled_feature_operations(self, operations):
        ext_props = self._get_service_extension_by_type("FeatureServer").find("./Info/PropertyArray")
        enabled_ops_prop = self._get_value_element_by_key(ext_props, "WebCapabilities")
        self._set_element_value(enabled_ops_prop, ",".join([o.title() for o in operations]))

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
        if isinstance(value, int):
            element.text = str(value)
            return
        if isinstance(value, bool):
            element.text = "true" if value == True else "false"
            return
        if isinstance(value, basestring):
            element.text = value
            return
        raise ValueError("Element value cannot be set, unknown type.")
    
    def _set_full_path_properties(self):
        """Sets the value for properties that are dependent on both the folder name and the service name."""
        wfs_ext_props = self._get_service_extension_by_type("WFSServer").find("./Props/PropertyArray").findall("PropertySetProperty")
        wfs_ext_name_props = self._get_value_elements_by_keys(wfs_ext_props, ["appSchemaPrefix"])
        for prop in wfs_ext_name_props:
            merged_value = "{0}_{1}".format(self.folder, self.name) if self.folder != None else self.name
            self._set_element_value(prop, merged_value)