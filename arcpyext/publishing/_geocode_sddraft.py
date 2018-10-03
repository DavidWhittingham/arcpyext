from __future__ import (absolute_import, division, print_function, unicode_literals)
from builtins import (bytes, dict, int, list, object, range, str, ascii, chr, hex, input, next, oct, open, pow, round,
                      super, filter, map, zip)

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