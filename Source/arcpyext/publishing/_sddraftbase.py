import codecs
import datetime
import re
import xml.etree.ElementTree as ET
import xml.dom.minidom as DOM

from abc import ABCMeta

from enum import Enum

class SDDraftBase:
    __metaclass__ = ABCMeta

    class Extension(Enum):
        """Must be overridden by sub-classes if any extensions are supported."""
        pass

    #############################
    # PRIVATE CONSTANTS/STATICS #
    #############################
    
    _TIME_STRING_REGEX = re.compile(r"^([0-9]{2}):([0-9]{2})$")
    
    # XML Keys
    _IDLE_TIMEOUT_KEY = "IdleTimeout"
    _INSTANCES_PER_CONTAINER_KEY = "InstancesPerContainer"
    _ISOLATION_KEY = "Isolation"
    _MAX_INSTANCES_KEY = "MaxInstances"
    _MIN_INSTANCES_KEY = "MinInstances"
    _RECYCLE_START_TIME_KEY = "recycleStartTime"
    _RECYCLE_INTERVAL_KEY = "recycleInterval"
    _USAGE_TIMEOUT_KEY = "UsageTimeout"
    _WAIT_TIMEOUT_KEY = "WaitTimeout"

    def __init__(self, path):
        self._path = path
        self._xmltree = self._parse_xmlns(path)

    #####################
    # PUBLIC PROPERTIES #
    #####################

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
    def enabled_extensions(self):
        """Gets a list of the extensions (by type name) that are currently enabled for the service."""
        exts = self._get_elements_by_tag("SVCExtension")
        return [self.Extension(self._get_element_value(item.find("TypeName"))) for item in exts
            if self._get_element_value(item.find("Enabled")).lower() == "true"]

            
    @enabled_extensions.setter
    def enabled_extensions(self, values):
        """Sets the extensions (by an iterable of type names) that are enabled for the service.

        Valid values are defined in the 'Extension' class on the concrete implementer.
        """
        types = []
        for val in values:
            if not isinstance(val, basestring):
                val = val.value
            val = val.lower()
            types.append(val)
        
        for ext in self._get_elements_by_tag("SVCExtension"):
            type = self._get_element_value(ext.find("TypeName"))
            if type.lower() in types:
                self._set_element_value(ext.find("Enabled"), "true")
            else:
                self._set_element_value(ext.find("Enabled"), "false")


    @property
    def file_path(self):
        """Gets the file path to the Service Definition Draft."""
        return self._path


    @property
    def folder(self):
        """Gets the name of the folder that the service will reside in."""
        folder_value = self._get_element_value(self._get_folder_element())
        return None if folder_value == "" else folder_value

    @folder.setter
    def folder(self, value):
        """Sets the name of the folder that the service will reside in."""
        value = "" if value == None else value
        self._set_element_value(self._get_folder_element(), value)


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


    @property
    def recycle_interval(self):
        """Gets the recycle interval (in hours)."""
        return self._get_int_value_from_element(self._get_recycle_interval_element())

    @recycle_interval.setter
    def recycle_interval(self, value):
        """Sets the recycle interval (in hours)."""
        self._set_int_value_to_element(value, self._get_recycle_interval_element(),
			"Recycle Interval", allow_none = True)


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
    def summary(self):
        """Gets the summary for the service."""
        return self._get_element_value(self._get_summary_element())

    @summary.setter
    def summary(self, value):
        """Sets the summary for the service."""
        self._set_element_value(self._get_summary_element(), value)


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

    def _value_to_boolean(self, value):
        """Converts true-ish and false-ish values to boolean."""
        try:
            value = value.upper()
            value = True if value in ["TRUE", "T"] else False
        except AttributeError:
            pass

        return value == True

    # Generic SD Draft Helpers
    def _get_description_element(self):
        item_info = self._get_first_element_by_tag("ItemInfo")
        return item_info.find("Description")

    def _get_folder_element(self):
        return self._get_first_element_by_tag("SVCConfiguration").find("ServiceFolder")

    def _get_idle_timeout_element(self):
        return self._get_value_element_by_key(self._get_service_props(), self._IDLE_TIMEOUT_KEY)

    def _get_instances_per_container_element(self):
        return self._get_value_element_by_key(self._get_service_props(), self._INSTANCES_PER_CONTAINER_KEY)
    
    def _get_int_value_from_element(self, element, required = False):
        value = self._get_element_value(element)
        if required:
            return int(value)
        else:
            return int(value) if value != None and value != "" else None

    def _get_isolation_element(self):
        return self._get_value_element_by_key(self._get_service_props(), self._ISOLATION_KEY)

    def _get_max_instances_element(self):
        return self._get_value_element_by_key(self._get_service_props(), self._MAX_INSTANCES_KEY)

    def _get_min_instances_element(self):
        return self._get_value_element_by_key(self._get_service_props(), self._MIN_INSTANCES_KEY)

    def _get_name_elements(self):
        sm_name = self._get_first_element_by_tag("SVCManifest").find("Name")
        sc_name = self._get_first_element_by_tag("SVCConfiguration").find("Name")

        return [sm_name, sc_name]

    def _get_recycle_start_time_element(self):
        return self._get_value_element_by_key(self._get_service_props(), self._RECYCLE_START_TIME_KEY)

    def _get_recycle_interval_element(self):
        return self._get_value_element_by_key(self._get_service_props(), self._RECYCLE_INTERVAL_KEY)

    def _get_service_config_props(self):
        return list(self._xmltree.getroot().find("./Configurations/SVCConfiguration/Definition/ConfigurationProperties/PropertyArray"))

    def _get_service_props(self):
        return list(self._xmltree.getroot().find("./Configurations/SVCConfiguration/Definition/Props/PropertyArray"))

    def _get_summary_element(self):
        item_info = self._get_first_element_by_tag("ItemInfo")
        return item_info.find("Snippet")

    def _get_usage_timeout_element(self):
        return self._get_value_element_by_key(self._get_service_props(), self._USAGE_TIMEOUT_KEY)

    def _get_wait_timeout_element(self):
        return self._get_value_element_by_key(self._get_service_props(), self._WAIT_TIMEOUT_KEY)

    def _get_value_element_by_key(self, prop_list, key):
        """ From a list of PropertySetProperty elements, return the "value" child element of the first
        PropertySetProperty element with a particular key."""
        return next(item.find("Value") for item in list(prop_list) if item.findtext("Key").lower() == key.lower())

    def _get_value_elements_by_keys(self, prop_list, keys):
        """ From a list of PropertySetProperty elements, returns a list of the "value" child elements of
        PropertySetProperty elements with a particular key."""
        return [item.find("Value") for item in list(prop_list) if item.findtext("Key") in keys]

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
        if value == None:
            element.text = None
            return
        if isinstance(value, bool):
            element.text = "true" if value == True else "false"
            return
        if isinstance(value, int):
            element.text = str(value)
            return
        if isinstance(value, basestring):
            element.text = value
            return
        raise ValueError("Element value cannot be set, unknown type.")

    def _set_int_value_to_element(self, value, element, name, allow_none = False, allow_negative = False):
        if allow_none == False and value == None:
            raise ValueError("{0} cannot be None.".format(name))
            
        if allow_negative == False and value != None and value < 0:
            raise ValueError("{0} cannot be less than zero.".format(name))
            
        self._set_element_value(element, value)