from _sddraft_base import SDDraftBase

class SDDraftCacheable(SDDraftBase):

    @property
    def cache_on_demand(self):
        """Gets a boolean value that descrbies if the service should generate cache tiles on demand."""
        return self._editor.value_to_boolean(self._editor.get_element_value(self._cache_on_demand_element))

    @cache_on_demand.setter
    def cache_on_demand(self, value):
        """Sets a boolean value that descrbies if the service should generate cache tiles on demand."""
        self._editor.set_element_value(self._cache_on_demand_element, self._editor.value_to_boolean(value))

    @property
    def keep_cache(self):
        """Gets a boolean value that describes if the service should keep its cache on publish."""
        return self._editor.value_to_boolean(self._editor.get_element_value(self._keep_existing_map_cache_element))

    @keep_cache.setter
    def keep_cache(self, value):
        """Sets a boolean value that describes if the service should keep its cache on publish."""
        self._editor.set_element_value(self._keep_existing_map_cache_element, self._editor.value_to_boolean(value))

    @property
    def export_tiles_allowed(self):
        """Gets a boolean value that describes if the service should allow tiles to be exported."""
        return self._editor.value_to_boolean(self._editor.get_element_value(self._export_tiles_allowed_element))

    @export_tiles_allowed.setter
    def export_tiles_allowed(self, value):
        """Sets a boolean value that describes if the service should allow tiles to be exported."""
        self._editor.set_element_value(self._export_tiles_allowed_element, self._editor.value_to_boolean(value))

    @property
    def max_export_tiles_count(self):
        """Gets an integer value that describes how many tiles can be expored."""
        return int(self._editor.get_element_value(self._max_export_tiles_count_element))

    @max_export_tiles_count.setter
    def max_export_tiles_count(self, value):
        """Sets an integer value that describes how many tiles can be expored."""
        value = int(value)

        if value < 0:
            raise ValueError("Max Export Tiles Count cannot be less than zero.")

        self._editor.set_element_value(self._max_export_tiles_count_element, value)

    @property
    def _cache_on_demand_element(self):
        return self._editor.get_value_element_by_key(self._config_props, "cacheOnDemand")

    @property
    def _export_tiles_allowed_element(self):
        return self._editor.get_value_element_by_key(self._config_props, "exportTilesAllowed")

    @property
    def _keep_existing_map_cache_element(self):
        return self._editor.get_first_element_by_tag("KeepExistingMapCache")

    @property
    def _max_export_tiles_count_element(self):
        return self._editor.get_value_element_by_key(self._config_props, "maxExportTilesCount")