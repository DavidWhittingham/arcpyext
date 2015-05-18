from ._sddraft_base import SDDraftBase

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

    def __init__(self, editor):
        super(GPSDDraft, self).__init__(editor)

    #region Properties

    @property
    def execution_type(self):
        return self.ExecutionType(self._editor.get_element_value(self._execution_type_elements[0]))

    @execution_type.setter
    def execution_type(self, value):
        if not isinstance(value, self.ExecutionType):
            value = self.ExecutionType(value)
        for elem in self._execution_type_elements:
            self._editor.set_element_value(elem, value.value)

    @property
    def result_map_server(self):
        return self._editor.value_to_boolean(self._editor.get_element_value(self._result_map_server_elements[0]))

    @result_map_server.setter
    def result_map_server(self, value):
        value = self._editor.value_to_boolean(value)
        for elem in self._result_map_server_elements:
            self._editor.set_element_value(elem, value)

    @property
    def show_messages(self):
        return self.MessageLevel(self._editor.get_element_value(self._show_messages_elements[0]))

    @show_messages.setter
    def show_messages(self, value):
        if not isinstance(value, self.MessageLevel):
            value = self.MessageLevel(value)
        for elem in self._show_messages_elements:
            self._editor.set_element_value(elem, value.value)

    @property
    def _execution_type_elements(self):
        return [
            self._editor.get_value_element_by_key(self._config_props, "executionType"),
            self._editor.get_value_element_by_key(self._service_props, "executionType")
        ]

    @property
    def _idle_timeout_elements(self):
        # Override.  GP SD Draft stores value in TWO PLACES!!!! Grrrr.
        elems = super(GPSDDraft, self)._idle_timeout_elements
        elems.append(self._editor.get_value_element_by_key(self._config_props, self._IDLE_TIMEOUT_KEY))
        return elems

    @property
    def _max_record_count_elements(self):
        # Override.  GP SD Draft stores value in TWO PLACES!!!! Grrrr.
        elems = super(GPSDDraft, self)._max_record_count_elements
        elems.append(self._editor.get_value_element_by_key(self._service_props, self._MAX_RECORD_COUNT_KEY))
        return elems

    @property
    def _max_instances_elements(self):
        # Override.  GP SD Draft stores value in TWO PLACES!!!! Grrrr.
        elems = super(GPSDDraft, self)._max_instances_elements
        elems.append(self._editor.get_value_element_by_key(self._config_props, self._MAX_INSTANCES_KEY))
        return elems

    @property
    def _min_instances_elements(self):
        # Override.  GP SD Draft stores value in TWO PLACES!!!! Grrrr.
        elems = super(GPSDDraft, self)._min_instances_elements
        elems.append(self._editor.get_value_element_by_key(self._config_props, self._MIN_INSTANCES_KEY))
        return elems

    @property
    def _result_map_server_elements(self):
        return [
            self._editor.get_value_element_by_key(self._config_props, "resultMapServer"),
            self._editor.get_value_element_by_key(self._service_props, "resultMapServer")
        ]

    @property
    def _show_messages_elements(self):
        return [
            self._editor.get_value_element_by_key(self._config_props, "showMessages"),
            self._editor.get_value_element_by_key(self._service_props, "showMessages")
        ]

    @property
    def _usage_timeout_elements(self):
        # Override. GP SD Draft stores value in TWO PLACES!!!! Grrrr.
        elems = super(GPSDDraft, self)._usage_timeout_elements
        elems.append(self._editor.get_value_element_by_key(self._config_props, self._USAGE_TIMEOUT_KEY))
        return elems

    @property
    def _wait_timeout_elements(self):
        # Override. GP SD Draft stores value in TWO PLACES!!!! Grrrr.
        elems = super(GPSDDraft, self)._wait_timeout_elements
        elems.append(self._editor.get_value_element_by_key(self._config_props, self._WAIT_TIMEOUT_KEY))
        return elems

    #endregion