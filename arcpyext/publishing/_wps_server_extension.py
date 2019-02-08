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


class WpsServerExtension(CustomGetCapabilitiesExtensionMixin, OgcMetadataExtensionMixin, SDDraftExtension):

    _ADMINISTRATIVE_AREA_KEY = "administrativeArea"
    _ADDRESS_KEY = "deliveryPoint"
    _CONTACT_INSTRUCTIONS_KEY = "contactInstructions"
    _EMAIL_KEY = "electronicMailAddress"
    _EXTENSION_TYPE = "WPSServer"
    _KEYWORD_KEY = "keyword"
    _KEYWORDS_TYPE_KEY = "keywordsType"
    _FACSIMILE_KEY = "facsimile"
    _FEES_KEY = "fee"
    _HOURS_OF_SERVICE_KEY = "hoursOfService"
    _INDIVIDUAL_NAME_KEY = "individualName"
    _NAME_KEY = "name"
    _ORGANIZATION_KEY = "providerName"
    _PHONE_KEY = "phone"
    _POSITION_NAME_KEY = "positionName"
    _POST_CODE_KEY = "postalCode"
    _PREFIX_KEY = "appSchemaPrefix"
    _PROFILE_KEY = "profile"
    _PROVIDER_SITE_KEY = "providerSite"
    _ROLE_KEY = "role"
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
    def capabilities(self):
        """JPIP Server Extension does not support capabilities.  Returns None, raises NotImplementedError on set."""
        return None

    @capabilities.setter
    def capabilities(self, values):
        raise NotImplementedError("No capabilities can be set for the JPIP Server Extension.")

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
    def hours_of_service(self):
        """Gets or sets the WFS namespace prefix that is used by the WFS GetFeatureRequest request.

        :type: str
        """
        return self._get_prop_value(self._HOURS_OF_SERVICE_KEY)

    @hours_of_service.setter
    def hours_of_service(self, value):
        self._set_prop_value(self._HOURS_OF_SERVICE_KEY, value)

    @property
    def keywords_type(self):
        """Gets or sets the keyword type value for the service.

        :type: str
        """
        return self._get_prop_value(self._KEYWORDS_TYPE_KEY)

    @keywords_type.setter
    def keywords_type(self, value):
        self._set_prop_value(self._KEYWORDS_TYPE_KEY, value)

    @property
    def profile(self):
        """Gets or sets the profile metadata value for the service.

        :type: str
        """
        return self._get_prop_value(self._PROFILE_KEY)

    @profile.setter
    def profile(self, value):
        self._set_prop_value(self._PROFILE_KEY, value)

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
    def role(self):
        """Gets or sets the role metadata value for the service.

        :type: str
        """
        return self._get_prop_value(self._ROLE_KEY)

    @role.setter
    def role(self, value):
        self._set_prop_value(self._ROLE_KEY, value)

    @property
    def service_type(self):
        """Gets or sets the service type for the service, e.g. 'WPS'.

        :type: str
        """
        return self._get_prop_value(self._SERVICE_TYPE_KEY)

    @service_type.setter
    def service_type(self, value):
        self._set_prop_value(self._SERVICE_TYPE_KEY, value)

    @property
    def service_type_version(self):
        """Gets or sets the service type version for the service, e.g. '1.0'.

        :type: str
        """
        return self._get_prop_value(self._SERVICE_TYPE_VERSION_KEY)

    @service_type_version.setter
    def service_type_version(self, value):
        self._set_prop_value(self._SERVICE_TYPE_VERSION_KEY, value)