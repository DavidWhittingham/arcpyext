from __future__ import (absolute_import, division, print_function, unicode_literals)
from builtins import (ascii, bytes, chr, dict, filter, hex, input, int, map, next, oct, open, pow,
                      range, round, str, super, zip)

from ._sddraft_extension import SDDraftExtension
from ._ogc_metadata_extension_mixin import OgcMetadataExtensionMixin
from ._custom_get_capabilities_extension_mixin import CustomGetCapabilitiesExtensionMixin

from enum import Enum


class WcsServerExtension(CustomGetCapabilitiesExtensionMixin, OgcMetadataExtensionMixin, SDDraftExtension):

    _EXTENSION_TYPE = "WCSServer"
    _ADMINISTRATIVE_AREA_KEY = "province"
    _ADDRESS_KEY = "address"
    _EMAIL_KEY = "email"
    _KEYWORD_KEY = "keywords"
    _FACSIMILE_KEY = "fax"
    _INDIVIDUAL_NAME_KEY = "responsiblePerson"
    _ORGANIZATION_KEY = "providerName"
    _PHONE_KEY = "phone"
    _POSITION_NAME_KEY = "responsiblePosition"
    _POST_CODE_KEY = "zipcode"

    @property
    def capabilities(self):
        """WCS Server Extension does not support capabilities.  Returns None, raises NotImplementedError on set."""
        return None

    @capabilities.setter
    def capabilities(self, values):
        raise NotImplementedError("No capabilities can be set for the Mobile Server Extension.")