# Python 2/3 compatibility
from __future__ import (absolute_import, division, print_function, unicode_literals)
from future.builtins import *
from future.builtins.disabled import *
from future.standard_library import install_aliases
install_aliases()

from ._sddraft_extension import SDDraftExtension
from ._ogc_metadata_extension_mixin import OgcMetadataExtensionMixin
from ._custom_get_capabilities_extension_mixin import CustomGetCapabilitiesExtensionMixin

from enum import Enum


class WfsServerExtension(CustomGetCapabilitiesExtensionMixin, OgcMetadataExtensionMixin, SDDraftExtension):

    class AxisOrder(Enum):
        lat_long = "LatLong"
        long_lat = "LongLat"

    _ADDRESS_KEY = "deliveryPoint"
    _ADMINISTRATIVE_AREA_KEY = "administrativeArea"
    _AXIS_ORDER_WFS_10_KEY = "axisOrderWFS10"
    _AXIS_ORDER_WFS_11_KEY = "axisOrderWFS11"
    _CONTACT_INSTRUCTIONS_KEY = "contactInstructions"
    _EMAIL_KEY = "electronicMailAddress"
    _ENABLE_TRANSACTIONS_KEY = "enableTransactions"
    _EXTENSION_TYPE = "WFSServer"
    _FACSIMILE_KEY = "facsimile"
    _HOURS_OF_SERVICE_KEY = "hoursOfService"
    _INDIVIDUAL_NAME_KEY = "individualName"
    _ORGANIZATION_KEY = "providerName"
    _PHONE_KEY = "phone"
    _POST_CODE_KEY = "postalCode"
    _POSITION_NAME_KEY = "positionName"
    _PREFIX_KEY = "appSchemaPrefix"
    _PROVIDER_SITE_KEY = "providerSite"
    _SERVICE_TYPE_KEY = "serviceType"
    _SERVICE_TYPE_VERSION_KEY = "serviceTypeVersion"

    @property
    def app_schema_prefix(self):
        """Gets or sets the WFS namespace prefix that is used by the WFS GetFeatureRequest request.

        :type: str
        """
        return self._get_prop_value(self._PREFIX_KEY)

    @app_schema_prefix.setter
    def app_schema_prefix(self, value):
        self._set_prop_value(self._PREFIX_KEY, value)

    @property
    def axis_order_wfs_10(self):
        """Gets or sets a the axis order for the WFS service when using the 1.0 API.

        :type: list(self.Capabilities)
        """
        return self.AxisOrder(self._get_prop_value(self._AXIS_ORDER_WFS_10_KEY))

    @axis_order_wfs_10.setter
    def axis_order_wfs_10(self, value):
        self._set_prop_value(
            self._AXIS_ORDER_WFS_10_KEY,
            self._editor.enum_to_str(value, self.AxisOrder, "Axis Order WFS 1.0 value is invalid."))

    @property
    def axis_order_wfs_11(self):
        """Gets or sets a the axis order for the WFS service when using the 1.1 API.

        :type: list(self.Capabilities)
        """
        return self.AxisOrder(self._get_prop_value(self._AXIS_ORDER_WFS_11_KEY))

    @axis_order_wfs_11.setter
    def axis_order_wfs_11(self, value):
        self._set_prop_value(
            self._AXIS_ORDER_WFS_11_KEY,
            self._editor.enum_to_str(value, self.AxisOrder, "Axis Order WFS 1.1 value is invalid."))

    @property
    def capabilities(self):
        """No capabilities are supported for WfsServerExtension. Returns None."""
        return None

    @capabilities.setter
    def capabilities(self, values):
        raise NotImplementedError("No capabilities can be set for the WFS Server Extension.")

    @property
    def contact_instructions(self):
        """Gets or sets instructions for appropriately contacting the organization and/or named person responsible
        for the service.

        :type: str
        """
        return self._get_prop_value(self._CONTACT_INSTRUCTIONS_KEY)

    @contact_instructions.setter
    def contact_instructions(self, value):
        self._set_prop_value(self._CONTACT_INSTRUCTIONS_KEY, value)

    @property
    def enable_transactions(self):
        """Gets or sets a value indicating whether or not layer names are inherited.

        :type: bool
        """
        return self._get_prop_value(self._ENABLE_TRANSACTIONS_KEY)

    @enable_transactions.setter
    def enable_transactions(self, value):
        self._set_prop_value(self._ENABLE_TRANSACTIONS_KEY, self._editor.value_to_boolean(value))

    @property
    def hours_of_service(self):
        """Gets or sets the WFS namespace prefix that is used by the WFS GetFeatureRequest request.

        :type: str
        """
        return self._get_prop_value(self._HOURS_OF_SERVICE_KEY)

    @hours_of_service.setter
    def hours_of_service(self, value):
        self._set_prop_value(self._HOURS_OF_SERVICE_KEY, value)

    @property
    def provider_site(self):
        """Gets or sets a URL to the provider's website.

        :type: str
        """
        return self._get_prop_value(self._PROVIDER_SITE_KEY)

    @provider_site.setter
    def provider_site(self, value):
        self._set_prop_value(self._PROVIDER_SITE_KEY, value)

    @property
    def service_type(self):
        """Gets or sets the service type for the service, e.g. 'WFS'.

        :type: str
        """
        return self._get_prop_value(self._SERVICE_TYPE_KEY)

    @service_type.setter
    def service_type(self, value):
        self._set_prop_value(self._SERVICE_TYPE_KEY, value)

    @property
    def service_type_version(self):
        """Gets or sets the service type version for the service, e.g. '1.1.0'.

        :type: str
        """
        return self._get_prop_value(self._SERVICE_TYPE_VERSION_KEY)

    @service_type_version.setter
    def service_type_version(self, value):
        self._set_prop_value(self._SERVICE_TYPE_VERSION_KEY, value)