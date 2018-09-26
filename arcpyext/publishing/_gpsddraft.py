from enum import Enum

from ._sddraft_base import SDDraftBase
from ._sddraft_output_dir import SDDraftOutputDirMixin
from ._wps_server_extension import WpsServerExtension

class GPSDDraft(SDDraftOutputDirMixin, SDDraftBase):

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

    #Override. MaxRecordCount key is completely different for a GP Service Draft. Why Esri, Why????
    _MAX_RECORD_COUNT_KEY = "maximumRecords"

    def __init__(self, editor):
        super(GPSDDraft, self).__init__(editor)
        self._wps_server_extension = WpsServerExtension(editor)

    #region Properties

    @property
    def execution_type(self):
        """Gets or sets the execution level for the service (as defined by the GPSDDraft.ExecutionType enumerated 
        type).

        """
        return self.ExecutionType(self._editor.get_element_value(self._execution_type_elements[0]))

    @execution_type.setter
    def execution_type(self, value):
        if not isinstance(value, self.ExecutionType):
            value = self.ExecutionType(value)
        for elem in self._execution_type_elements:
            self._editor.set_element_value(elem, value.value)

    @property
    def folder(self):
        """Gets or sets the name of the folder that the service will reside in."""
        return super(GPSDDraft, self).folder

    @folder.setter
    def folder(self, value):
        existing_full_path = self._get_full_path()
        SDDraftBase.folder.fset(self, value)
        self._set_full_path_properties(existing_full_path, self._get_full_path())

    @property
    def name(self):
        """Gets or sets the name of the service."""
        return super(GPSDDraft, self).name

    @name.setter
    def name(self, value):
        existing_full_path = self._get_full_path()

        # Set the underlying value from base class and then update properties that are built from the full path
        SDDraftBase.name.fset(self, value)
        self._set_full_path_properties(existing_full_path, self._get_full_path())

    @property
    def result_map_server(self):
        """Gets or sets a value indicating whether or not the results should be viewed with a map service.

        :type: bool
        """
        return self._editor.value_to_boolean(
            self._editor.get_element_value(self._result_map_server_elements[0]))

    @result_map_server.setter
    def result_map_server(self, value):
        value = self._editor.value_to_boolean(value)
        for elem in self._result_map_server_elements:
            self._editor.set_element_value(elem, value)

    @property
    def show_messages(self):
        """Gets or sets a value indicating what level of messaging should be shown with the service.

        :type: GPSDDraft.MessageLevel
        """
        return self.MessageLevel(self._editor.get_element_value(self._show_messages_elements[0]))

    @show_messages.setter
    def show_messages(self, value):
        if not isinstance(value, self.MessageLevel):
            value = self.MessageLevel(value)
        for elem in self._show_messages_elements:
            self._editor.set_element_value(elem, value.value)

    @property
    def wps_server(self):
        return self._wps_server_extension

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

    #region Methods

    def _set_full_path_properties(self, old_path, new_path):
        """Sets the value for properties that are dependent on both the folder name and the service name.

        Only sets the values if they haven't been changed from the default "folder_name" value.
        """
        if self.wps_server.app_schema_prefix == old_path:
            self.wps_server.app_schema_prefix = new_path

    def _get_full_path(self):
        return "{0}_{1}".format(self.folder, self.name) if self.folder != None else self.name

    #endregion
