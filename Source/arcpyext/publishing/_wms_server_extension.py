from __future__ import (absolute_import, division, print_function, unicode_literals)
from builtins import (ascii, bytes, chr, dict, filter, hex, input, int, map, next, oct, open, pow,
                      range, round, str, super, zip)

from ._sddraft_extension import SDDraftExtension
from ._ogc_metadata_extension_mixin import OgcMetadataExtensionMixin
from ._custom_get_capabilities_extension_mixin import CustomGetCapabilitiesExtensionMixin

from enum import Enum


class WmsServerExtension(CustomGetCapabilitiesExtensionMixin, OgcMetadataExtensionMixin, SDDraftExtension):

    class Capability(Enum):
        get_capabilities = "GetCapabilities"
        get_map = "GetMap"
        get_feature_info = "GetFeatureInfo"
        get_styles = "GetStyles"
        get_legend_graphic = "GetLegendGraphic"
        get_schema_extension = "GetSchemaExtension"

    _ADDRESS_KEY = "address"
    _ADDRESS_TYPE_KEY = "addressType"
    _ADMINISTRATIVE_AREA_KEY = "stateOrProvince"
    _EMAIL_KEY = "contactElectronicMailAddress"
    _EXTENSION_TYPE = "WMSServer"
    _FACSIMILE_KEY = "contactFacsimileTelephone"
    _ORGANIZATION_KEY = "contactOrganization"
    _INDIVIDUAL_NAME_KEY = "contactPerson"
    _POSITION_NAME_KEY = "contactPosition"
    _PHONE_KEY = "contactVoiceTelephone"
    _INHERIT_LAYER_NAMES_KEY = "inheritLayerNames"
    _PATH_TO_CUSTOM_SLD_FILE_KEY = "pathToCustomSLDFile"
    _POST_CODE_KEY = "postCode"

    # region Constructor(s)

    def __init__(self, editor):
        super(WmsServerExtension, self).__init__(editor)

    # endregion

    # region Properties

    @property
    def address_type(self):
        """Gets or sets the address type metadata value for the WMS service.

        :type: str
        """
        return self._get_prop_value(self._ADDRESS_TYPE_KEY)

    @address_type.setter
    def address_type(self, value):
        self._set_prop_value(self._ADDRESS_TYPE_KEY, value)

    @property
    def inherit_layer_names(self):
        """Gets or sets a value indicating whether or not layer names are inherited.

        :type: bool
        """
        return self._get_prop_value(self._INHERIT_LAYER_NAMES_KEY)

    @inherit_layer_names.setter
    def inherit_layer_names(self, value):
        self._set_prop_value(self._INHERIT_LAYER_NAMES_KEY, self._editor.value_to_boolean(value))

    @property
    def path_to_custom_sld_file(self):
        """Gets or sets the path to the custom Styled Layer Descriptor (SLD) file.

        The path should be a URL or path accessible by ArcGIS Server.

        :type: str
        """
        return self._get_prop_value(self._PATH_TO_CUSTOM_SLD_FILE_KEY)

    @path_to_custom_sld_file.setter
    def path_to_custom_sld_file(self, value):
        self._set_prop_value(self._PATH_TO_CUSTOM_SLD_FILE_KEY, value)

    # endregion