# Python 2/3 compatibility
from __future__ import (absolute_import, division, print_function, unicode_literals)
from future.builtins import *
from future.builtins.disabled import *
from future.standard_library import install_aliases
install_aliases()

from ._sddraft_base import SDDraftBase

class SDDraftMaxRecordCountMixin(SDDraftBase):

    # XML Keys
    _MAX_RECORD_COUNT_KEY = "maxRecordCount"

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
    def _max_record_count_elements(self):
        return [self._editor.get_value_element_by_key(self._config_props, self._MAX_RECORD_COUNT_KEY)]