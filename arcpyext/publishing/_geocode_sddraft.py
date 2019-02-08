# Python 2/3 compatibility
from __future__ import (absolute_import, division, print_function, unicode_literals)
from future.builtins import *
from future.builtins.disabled import *
from future.standard_library import install_aliases
install_aliases()

from enum import Enum

from ._sddraft_base import SDDraftBase

class GeocodeSDDraft(SDDraftBase):

    class Capability(Enum):
        geocode = "Geocode"
        reverse_geocode = "ReverseGeocode"

    @property
    def _name_elements(self):
        return super()._name_elements + [
            self._item_info_element.find("Name"),
            self._item_info_element.find("Title")
        ]

    @property
    def _capabilities_element(self):
        return self._editor.get_value_element_by_key(self._info_props, "webCapabilities")