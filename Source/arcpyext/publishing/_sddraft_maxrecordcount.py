from ._sddraftbase import SDDraftBase

class SDDraftMaxRecordCount(SDDraftBase):
    _MAX_RECORD_COUNT_KEY = "maxRecordCount"

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

    def _get_max_record_count_element(self):
        return self._get_value_element_by_key(self._get_service_config_props(), self._MAX_RECORD_COUNT_KEY)