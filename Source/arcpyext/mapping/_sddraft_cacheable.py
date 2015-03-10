from _sddraftbase import SDDraftBase

class SDDraftCacheable(SDDraftBase):

    @property
    def keep_cache(self):
        """Gets a boolean value that describes if the service should keep its cache on publish."""
        return self._value_to_boolean(self._get_element_value(self._get_first_element_by_tag("KeepExistingMapCache")))

    @keep_cache.setter
    def keep_cache(self, value):
        """Sets a boolean value that describes if the service should keep its cache on publish."""
        value = self._value_to_boolean(value)

        self._set_element_value(self._get_first_element_by_tag("KeepExistingMapCache"), value)