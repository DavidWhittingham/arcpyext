from _sddraft_base import SDDraftBase

class SDDraftCacheable(SDDraftBase):

    @property
    def keep_cache(self):
        """Gets a boolean value that describes if the service should keep its cache on publish."""
        return self._editor.value_to_boolean(self._editor.get_element_value(self._editor.get_first_element_by_tag("KeepExistingMapCache")))

    @keep_cache.setter
    def keep_cache(self, value):
        """Sets a boolean value that describes if the service should keep its cache on publish."""
        value = self._editor.value_to_boolean(value)

        self._editor.set_element_value(self._editor.get_first_element_by_tag("KeepExistingMapCache"), value)