from ._sddraftbase import SDDraftBase

from enum import Enum

class GPSDDraft(SDDraftBase):

    class Capability(Enum):
        uploads = "Uploads"

    class ExecutionType(Enum):
        synchronous = "Synchronous"
        asynchronous = "Asynchronous"

    class MessageLevel(Enum):
        none = "None"
        error = "Error"
        warning = "Warning"
        info = "Info"

    class Extension(Enum):
        wpsserver = "WPSServer"

    #Override. MaxRecordCount key is completely different for a GP Service Draft. Why Esri, Why????
    _MAX_RECORD_COUNT_KEY = "maximumRecords"

    def __init__(self, path):
        super(GPSDDraft, self).__init__(path)

    #####################
    # PUBLIC PROPERTIES #
    #####################

    @property
    def capabilities(self):
        """Gets a list of GPSDDraft.Capability objects supported by the GP service."""
        value = self._get_element_value(self._get_capabilities_element())
        if value != None and value != "":
            return [self.Capability(val) for val in value.split(",")]
        else:
            return []

    @capabilities.setter
    def capabilities(self, values):
        """Sets a list of GPSDDraft.Capability objects supported by the GP service."""
        self._set_enum_val_list_to_element(
            values,
            self.Capability,
            self._get_capabilities_element(),
            "Capabilities specified are of an unknown type.")

    @property
    def execution_type(self):
        return self.ExecutionType(self._get_element_value(self._get_execution_type_elements()[0]))

    @execution_type.setter
    def execution_type(self, value):
        if not isinstance(value, self.ExecutionType):
            value = self.ExecutionType(value)
        for elem in self._get_execution_type_elements():
            self._set_element_value(elem, value.value)

    @property
    def result_map_server(self):
        return self._value_to_boolean(self._get_element_value(self._get_result_map_server_elements()[0]))

    @result_map_server.setter
    def result_map_server(self, value):
        value = self._value_to_boolean(value)
        for elem in self._get_result_map_server_elements():
            self._set_element_value(elem, value)

    @property
    def show_messages(self):
        return self.MessageLevel(self._get_element_value(self._get_show_messages_elements()[0]))

    @show_messages.setter
    def show_messages(self, value):
        if not isinstance(value, self.MessageLevel):
            value = self.MessageLevel(value)
        for elem in self._get_show_messages_elements():
            self._set_element_value(elem, value.value)

    ######################
    # PRIVATE PROPERTIES #
    ######################
    
    def _get_capabilities_element(self):
        return self._get_value_element_by_key(self._get_info_props(), "WebCapabilities")

    def _get_execution_type_elements(self):
        return [
            self._get_value_element_by_key(self._get_service_config_props(), "executionType"),
            self._get_value_element_by_key(self._get_service_props(), "executionType")
        ]

    def _get_max_instances_elements(self):
        # Override.  GP SD Draft stores value in TWO PLACES!!!! Grrrr.
        elems = super(GPSDDraft, self)._get_max_instances_elements()
        elems.append(self._get_value_element_by_key(self._get_service_config_props(), self._MAX_INSTANCES_KEY))
        return elems

    def _get_max_record_count_elements(self):
        # Override.  GP SD Draft stores value in TWO PLACES!!!! Grrrr.
        elems = super(GPSDDraft, self)._get_max_record_count_elements()
        elems.append(self._get_value_element_by_key(self._get_service_props(), self._MAX_RECORD_COUNT_KEY))
        return elems

    def _get_min_instances_elements(self):
        # Override.  GP SD Draft stores value in TWO PLACES!!!! Grrrr.
        elems = super(GPSDDraft, self)._get_min_instances_elements()
        elems.append(self._get_value_element_by_key(self._get_service_config_props(), self._MIN_INSTANCES_KEY))
        return elems

    def _get_idle_timeout_elements(self):
        # Override.  GP SD Draft stores value in TWO PLACES!!!! Grrrr.
        elems = super(GPSDDraft, self)._get_idle_timeout_elements()
        elems.append(self._get_value_element_by_key(self._get_service_config_props(), self._IDLE_TIMEOUT_KEY))
        return elems

    def _get_result_map_server_elements(self):
        return [
            self._get_value_element_by_key(self._get_service_config_props(), "resultMapServer"),
            self._get_value_element_by_key(self._get_service_props(), "resultMapServer")
        ]

    def _get_show_messages_elements(self):
        return [
            self._get_value_element_by_key(self._get_service_config_props(), "showMessages"),
            self._get_value_element_by_key(self._get_service_props(), "showMessages")
        ]

    def _get_usage_timeout_elements(self):
        # Override. GP SD Draft stores value in TWO PLACES!!!! Grrrr.
        elems = super(GPSDDraft, self)._get_usage_timeout_elements()
        elems.append(self._get_value_element_by_key(self._get_service_config_props(), self._USAGE_TIMEOUT_KEY))
        return elems

    def _get_wait_timeout_elements(self):
        elems = super(GPSDDraft, self)._get_wait_timeout_elements()
        elems.append(self._get_value_element_by_key(self._get_service_config_props(), self._WAIT_TIMEOUT_KEY))
        return elems