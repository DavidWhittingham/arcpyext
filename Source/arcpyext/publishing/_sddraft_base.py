import datetime
import re

from abc import ABCMeta
from decimal import Decimal

from enum import Enum

from ._svc_resource import SVCResource

class SDDraftBase():
    __metaclass__ = ABCMeta

    class Capability(Enum):
        """Must be overridden by sub-classes if any capabilities are supported."""
        pass

    class Extension(Enum):
        """Must be overridden by sub-classes if any extensions are supported."""
        pass

    #region Constants/Statics

    #: A regular expression for matching time notation
    _TIME_STRING_REGEX = re.compile(r"^([0-9]{2}):([0-9]{2})$")

    # XML Keys
    _IDLE_TIMEOUT_KEY = "IdleTimeout"
    _INSTANCES_PER_CONTAINER_KEY = "InstancesPerContainer"
    _ISOLATION_KEY = "Isolation"
    _MAX_INSTANCES_KEY = "MaxInstances"
    _MAX_RECORD_COUNT_KEY = "maxRecordCount"
    _MAX_SCALE_KEY = "maxScale"
    _MIN_INSTANCES_KEY = "MinInstances"
    _MIN_SCALE_KEY = "minScale"
    _OUTPUT_DIR_KEY = "outputDir"
    _RECYCLE_START_TIME_KEY = "recycleStartTime"
    _RECYCLE_INTERVAL_KEY = "recycleInterval"
    _RESOURCES_KEY = "Resources"
    _USAGE_TIMEOUT_KEY = "UsageTimeout"
    _VIRTUAL_OUTPUT_DIR_KEY = "virtualOutputDir"
    _WAIT_TIMEOUT_KEY = "WaitTimeout"

    #endregion

    #region Constructor(s)

    def __init__(self, editor):
        self._editor = editor
        self._resources = None

    #endregion

    #region Properties

    @property
    def access_information(self):
        """Gets the value of the access_information attribute for the service."""
        return self._editor.get_element_value(self._editor.get_first_element_by_tag("AccessInformation", self._item_info_element))

    @access_information.setter
    def access_information(self, value):
        """Sets the value of the access_information attribute for the service."""
        self._editor.set_element_value(self._editor.get_first_element_by_tag("AccessInformation", self._item_info_element), value)

    @property
    def capabilities(self):
        """Gets or sets a list of capabilities (as defined by self.Capability enumerator) that are enabled for this
        service.

        :type: list(self.Capability)
        """
        value = self._editor.get_element_value(self._capabilities_element)
        if value != None and value != "":
            return [self.Capability(val) for val in value.split(",")]
        else:
            return []

    @capabilities.setter
    def capabilities(self, values):
        self._editor.set_element_value(
            self._capabilities_element,
            self._editor.enum_list_to_str(values, self.Capability, "Capabilities specified are of an unknown type."))

    @property
    def cluster(self):
        """Gets the name of the cluster that the published service will run on."""
        return self._editor.get_element_value(self._editor.get_first_element_by_tag("Cluster"))

    @cluster.setter
    def cluster(self, value):
        """Sets the name of the cluster that the published service will run on."""
        self._editor.set_element_value(self._editor.get_first_element_by_tag("Cluster"), value)

    @property
    def credits(self):
        """Gets the value of the credits attribute for the service."""
        return self._editor.get_element_value(self._editor.get_first_element_by_tag("Credits", self._item_info_element))

    @credits.setter
    def credits(self, value):
        """Sets the value of the credits attribute for the service."""
        self._editor.set_element_value(self._editor.get_first_element_by_tag("Credits", self._item_info_element), value)

    @property
    def description(self):
        """Gets the description for the service."""
        return self._editor.get_element_value(self._description_elements[0])

    @description.setter
    def description(self, value):
        """Sets the description for the service."""
        for elem in self._description_elements:
            self._editor.set_element_value(elem, value)

    @property
    def file_path(self):
        """Gets the file path to the Service Definition Draft."""
        return self._editor.file_path

    @property
    def folder(self):
        """Gets the name of the folder that the service will reside in."""
        folder_value = self._editor.get_element_value(self._folder_element)
        return None if folder_value == "" else folder_value

    @folder.setter
    def folder(self, value):
        """Sets the name of the folder that the service will reside in."""
        value = "" if value == None else value
        self._editor.set_element_value(self._folder_element, value)

    @property
    def high_isolation(self):
        """Gets a boolean that describes if the service is set to high isolation (true) or low isolation (false)."""
        isolation = self._editor.get_element_value(self._isolation_element)
        return True if isolation.upper() == "HIGH" else False

    @high_isolation.setter
    def high_isolation(self, value):
        """Sets a boolean that describes if the service is set to high isolation (true) or low isolation (false)."""
        self._editor.set_element_value(self._isolation_element,
            "HIGH" if value == True else "LOW")

    @property
    def idle_timeout(self):
        """Gets the idle timeout (in seconds) for the service."""
        return int(self._editor.get_element_value(self._idle_timeout_elements[0]))

    @idle_timeout.setter
    def idle_timeout(self, value):
        """Sets the idle timeout (in seconds) for the service."""
        if value < 0:
            raise ValueError("Timeout cannot be less than zero.")
        for elem in self._idle_timeout_elements:
            self._editor.set_element_value(elem, value)

    @property
    def instances_per_container(self):
        """Gets the number of instances of this service can run per container (i.e. process).

        Only applicable when running in low isolation.
        """
        return int(self._editor.get_element_value(self._instances_per_container_element))

    @instances_per_container.setter
    def instances_per_container(self, value):
        """Sets the number of instances of this service can run per container (i.e. process).

        Only applicable when running in low isolation.
        """
        self._editor.set_element_value(self._instances_per_container_element, value)

    @property
    def max_instances(self):
        """Gets the maximum number of instances that the published service will run."""
        return int(self._editor.get_element_value(self._max_instances_elements[0]))

    @max_instances.setter
    def max_instances(self, value):
        """Sets the maximum number of instances that the published service will run."""
        if value <= 0:
            raise ValueError("Max instances cannot be equal to or less than zero.")

        for elem in self._max_instances_elements:
            self._editor.set_element_value(elem, value)

        if value < self.min_instances:
            # Max instances can't be smaller than min instances, so make the same size
            self.min_instances = value

    @property
    def max_record_count(self):
        """Gets the maximum number of records that can be returned by the service."""
        return int(self._editor.get_element_value(self._max_record_count_elements[0]))

    @max_record_count.setter
    def max_record_count(self, value):
        """Sets the maximum number of records that can be returned by the service."""
        if value < 0:
            raise ValueError("Maximum record count cannot be less than zero.")
        for elem in self._max_record_count_elements:
            self._editor.set_element_value(elem, value)

    @property
    def max_scale(self):
        """Gets the maximum scale for this service."""
        return Decimal(self._editor.get_element_value(self._max_scale_element))

    @max_scale.setter
    def max_scale(self, value):
        """Sets the maximum scale for this service."""
        self._editor.set_element_value(self._max_scale_element, Decimal(value))

    @property
    def min_instances(self):
        """Gets the minimum number of instances that the published service will run."""
        return int(self._editor.get_element_value(self._min_instances_elements[0]))

    @min_instances.setter
    def min_instances(self, value):
        """Sets the minimum number of instances that the published service will run."""
        if value < 0:
            raise ValueError("Min instances cannot be less than zero.")

        for elem in self._min_instances_elements:
            self._editor.set_element_value(elem, value)

        if value > self.max_instances:
            # Min instances can't be bigger than max instances, so make the same size
            self.max_instances = value

    @property
    def min_scale(self):
        """Gets the maximum scale for this service."""
        return Decimal(self._editor.get_element_value(self._min_scale_element))

    @min_scale.setter
    def min_scale(self, value):
        """Sets the maximum scale for this service."""
        self._editor.set_element_value(self._min_scale_element, Decimal(value))

    @property
    def name(self):
        """Gets the name of the service."""
        name_props = self._name_elements
        return self._editor.get_element_value(name_props[0])

    @name.setter
    def name(self, value):
        """Sets the name of the service (Cannot be an empty value)."""
        if value == "":
            raise ValueError("Name string cannot be empty")
        for prop in self._name_elements:
            self._editor.set_element_value(prop, value)

    @property
    def output_dir(self):
        """Gets the output directory for the service."""
        output_dir_element = self._output_dir_element
        if not output_dir_element:
            return None

        return self._editor.get_element_value(output_dir_element)

    @output_dir.setter
    def output_dir(self, value):
        """Sets the output directory for the service.  This is paired with the virtual output directory property."""
        output_dir_element = self._output_dir_element
        if not output_dir_element:
            # Create an outputDir element and append it to the configuration properties
            self._editor.append_element(
                self._config_props,
                self._editor.create_config_element(self._OUTPUT_DIR_KEY, value))
        else:
            self._editor.set_element_value(output_dir_element, value)

    @property
    def recycle_interval(self):
        """Gets the recycle interval (in hours)."""
        return self._editor.get_element_value(self._recycle_interval_element)

    @recycle_interval.setter
    def recycle_interval(self, value):
        """Sets the recycle interval (in hours)."""
        self._editor.set_element_value(
            self._recycle_interval_element,
            self._editor.verify_int(value, "Recycle Interval", allow_none = True))

    @property
    def recycle_start_time(self):
        """Gets the recycle time for the service.

        Returns:
         - Recycle time for the service as a 'datetime.time' object
        """
        time = self._editor.get_element_value(self._recycle_start_time_element)
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
                self._editor.set_element_value(self._recycle_start_time_element, value)
            else:
                raise ValueError("Time string in incorrect format, must be in format 'hh:mm'.")
        else:
            value = "{0:02d}:{1:02d}".format(value.hour, value.minute)
            self._editor.set_element_value(self._recycle_start_time_element, value)

    @property
    def replace_existing(self):
        """Gets a boolean indicating whether or not a service of the same name will be replaced on publish."""
        manifest_type = self._editor.get_first_element_by_tag("Type")
        if self._editor.get_element_value(self._editor.get_first_element_by_tag("Type")) == "esriServiceDefinitionType_New":
            return False
        else:
            return True

    @replace_existing.setter
    def replace_existing(self, value):
        """Sets a boolean indicating whether or not a service of the same name will be replaced on publish."""
        value = self._editor.value_to_boolean(value)
        manifest_type = self._editor.get_first_element_by_tag("Type")
        self._editor.set_element_value(
            manifest_type,
            "esriServiceDefinitionType_Replacement" if value == True else "esriServiceDefinitionType_New")

    @property
    def resources(self):
        if self._resources == None:
            self._resources = [SVCResource(self._editor, elem) for elem in self._editor.get_first_element_by_tag("Resources")]
        return self._resources

    @property
    def summary(self):
        """Gets the summary for the service."""
        return self._editor.get_element_value(self._summary_element)

    @summary.setter
    def summary(self, value):
        """Sets the summary for the service."""
        self._editor.set_element_value(self._summary_element, value)

    @property
    def usage_timeout(self):
        """Gets the usage timeout (in seconds) for the service."""
        return int(self._editor.get_element_value(self._usage_timeout_elements[0]))

    @usage_timeout.setter
    def usage_timeout(self, value):
        """Sets the usage timeout (in seconds) for the service."""
        if value < 0:
            raise ValueError("Timeout cannot be less than zero.")
        for elem in self._usage_timeout_elements:
            self._editor.set_element_value(elem, value)

    @property
    def virtual_output_dir(self):
        """Gets the virtual output directory for the service."""
        virtual_output_dir_element = self._virtual_output_dir_element
        if not virtual_output_dir_element:
            return None

        return self._editor.get_element_value(virtual_output_dir_element)

    @virtual_output_dir.setter
    def virtual_output_dir(self, value):
        """Sets the virtual output directory for the service.  This is paired with the output directory property."""
        virtual_output_dir_element = self._output_dir_element
        if not virtual_output_dir_element:
            # Create a virtualOutputDir element and append it to the configuration properties
            self._editor.append_element(
                self._config_props,
                self._editor.create_config_element(self._VIRTUAL_OUTPUT_DIR_KEY, value))
        else:
            self._editor.set_element_value(virtual_output_dir_element, value)

    @property
    def wait_timeout(self):
        """Gets the wait timeout (in seconds) for the service."""
        return int(self._editor.get_element_value(self._wait_timeout_elements[0]))

    @wait_timeout.setter
    def wait_timeout(self, value):
        """Sets the wait timeout (in seconds) for the service."""
        if value < 0:
            raise ValueError("Timeout cannot be less than zero.")
        for elem in self._wait_timeout_elements:
            self._editor.set_element_value(elem, value)

    @property
    def _capabilities_element(self):
        return self._editor.get_value_element_by_key(self._info_props, "WebCapabilities")

    @property
    def _config_props(self):
        return self._service_config.find("./Definition/ConfigurationProperties/PropertyArray")

    @property
    def _description_elements(self):
        return [
            self._editor.get_first_element_by_tag("ItemInfo").find("Description"),
            self._editor.get_first_element_by_tag("Definition").find("Description")
        ]

    @property
    def _folder_element(self):
        return self._editor.get_first_element_by_tag("SVCConfiguration").find("ServiceFolder")

    @property
    def _idle_timeout_elements(self):
        return [self._editor.get_value_element_by_key(self._service_props, self._IDLE_TIMEOUT_KEY)]

    @property
    def _item_info_element(self):
        return self._editor.get_first_element_by_tag("ItemInfo")

    @property
    def _info_props(self):
        return list(self._service_config.find("./Definition/Info/PropertyArray"))

    @property
    def _instances_per_container_element(self):
        return self._editor.get_value_element_by_key(self._service_props, self._INSTANCES_PER_CONTAINER_KEY)

    @property
    def _isolation_element(self):
        return self._editor.get_value_element_by_key(self._service_props, self._ISOLATION_KEY)

    @property
    def _max_instances_elements(self):
        return [self._editor.get_value_element_by_key(self._service_props, self._MAX_INSTANCES_KEY)]

    @property
    def _max_record_count_elements(self):
        return [self._editor.get_value_element_by_key(self._config_props, self._MAX_RECORD_COUNT_KEY)]

    @property
    def _max_scale_element(self):
        return self._editor.get_value_element_by_key(self._config_props, self._MAX_SCALE_KEY)

    @property
    def _min_instances_elements(self):
        return [self._editor.get_value_element_by_key(self._service_props, self._MIN_INSTANCES_KEY)]

    @property
    def _min_scale_element(self):
        return self._editor.get_value_element_by_key(self._config_props, self._MIN_SCALE_KEY)

    @property
    def _name_elements(self):
        return [
            self._editor.get_first_element_by_tag("SVCManifest").find("Name"),
            self._editor.get_first_element_by_tag("SVCConfiguration").find("Name")
        ]

    @property
    def _output_dir_element(self):
        self._editor.get_value_element_by_key(self._config_props, self._OUTPUT_DIR_KEY)

    @property
    def _recycle_interval_element(self):
        return self._editor.get_value_element_by_key(self._service_props, self._RECYCLE_INTERVAL_KEY)

    @property
    def _recycle_start_time_element(self):
        return self._editor.get_value_element_by_key(self._service_props, self._RECYCLE_START_TIME_KEY)

    @property
    def _service_config(self):
        return self._editor.xmlroot.find("./Configurations/SVCConfiguration")

    @property
    def _service_props(self):
        return list(self._service_config.find("./Definition/Props/PropertyArray"))

    @property
    def _summary_element(self):
        return self._item_info_element.find("Snippet")

    @property
    def _usage_timeout_elements(self):
        return [self._editor.get_value_element_by_key(self._service_props, self._USAGE_TIMEOUT_KEY)]

    @property
    def _virtual_output_dir_element(self):
        self._editor.get_value_element_by_key(self._config_props, self._VIRTUAL_OUTPUT_DIR_KEY)

    @property
    def _wait_timeout_elements(self):
        return [self._editor.get_value_element_by_key(self._service_props, self._WAIT_TIMEOUT_KEY)]

    #endregion

    #region Methods

    def save(self):
        """Saves changes to the Service Definition Draft back to the file."""
        self._editor.save()

    def save_a_copy(self, path):
        """Saves a copy of the Service Definition Draft to a new file."""
        self._editor.save_a_copy(path)

    def _set_props_from_dict(self, prop_dict):
        """Method for setting properties from a dictionary where keys match property names.

        Can be overridden by sub-classes.
        """
        for k, v in prop_dict.items():
            if hasattr(self, k):
                try:
                    setattr(self, k, v)
                except AttributeError:
                    getattr(self, k)._set_props_from_dict(v)

    #endregion