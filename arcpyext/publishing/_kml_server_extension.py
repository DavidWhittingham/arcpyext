# Python 2/3 compatibility
from __future__ import (absolute_import, division, print_function, unicode_literals)
from future.builtins import *
from future.builtins.disabled import *
from future.standard_library import install_aliases
install_aliases()

from ._sddraft_extension import SDDraftExtension

from enum import Enum


class KmlServerExtension(SDDraftExtension):

    class Capability(Enum):
        single_image = "SingleImage"
        separate_images = "SeparateImages"
        vectors = "Vectors"

    class CompatibilityMode(Enum):
        google_earth = "GoogleEarth"
        google_maps = "GoogleMaps"
        google_mobile = "GoogleMobile"

    _COMPATIBILITY_MODE_KEY = "compatibilityMode"
    _DPI_KEY = "dpi"
    _FEATURE_LIMIT_KEY = "featureLimit"
    _EXTENSION_TYPE = "KmlServer"
    _IMAGE_SIZE_KEY = "imageSize"
    _LINK_DESCRIPTION_KEY = "linkDescription"
    _LINK_NAME_KEY = "linkName"
    _MESSAGE_KEY = "message"
    _MIN_REFRESH_PERIOD_KEY = "minRefreshPeriod"
    _USE_DEFAULT_SNIPPETS_KEY = "useDefaultSnippets"
    _USE_NETWORK_LINK_CONTROL_TAG_KEY = "useNetworkLinkControlTag"

    @property
    def compatibility_mode(self):
        """Gets or sets the compatibility mode (as defined by the KmlServerExtension.CompatibilityMode enumerator)
        for this service.

        :type: self.CompatibilityMode
        """
        return self.CompatibilityMode(self._get_prop_value(self._COMPATIBILITY_MODE_KEY))

    @compatibility_mode.setter
    def compatibility_mode(self, value):
        self._set_prop_value(
            self._COMPATIBILITY_MODE_KEY,
            self._editor.enum_to_str(value, self.CompatibilityMode, "Compatibility Mode is invalid."))

    @property
    def dpi(self):
        """Gets or sets the DPI for the service.

        :type: int
        """
        return self._get_prop_value(self._DPI_KEY)

    @dpi.setter
    def dpi(self, value):
        self._set_prop_value(
            self._DPI_KEY,
            self._editor.verify_int(value, "DPI", allow_zero = False))

    @property
    def feature_limit(self):
        """Gets or sets the maximum number of features that can be returned by the service.

        :type: int
        """
        return self._get_prop_value(self._FEATURE_LIMIT_KEY)

    @feature_limit.setter
    def feature_limit(self, value):
        self._set_prop_value(
            self._FEATURE_LIMIT_KEY,
            self._editor.verify_int(value, "feature limit"))

    @property
    def image_size(self):
        """Gets or sets the maximum image size (in either dimension).

        :type: int
        """
        return self._get_prop_value(self._IMAGE_SIZE_KEY)

    @image_size.setter
    def image_size(self, value):
        self._set_prop_value(
            self._IMAGE_SIZE_KEY,
            self._editor.verify_int(value, "image size"))

    @property
    def link_name(self):
        """Gets or sets the link name for the KML service.

        :type: str
        """
        return self._get_prop_value(self._LINK_NAME_KEY)

    @link_name.setter
    def link_name(self, value):
        self._set_prop_value(self._LINK_NAME_KEY, value)

    @property
    def link_description(self):
        """Gets or sets the link name for the KML service.

        :type: str
        """
        return self._get_prop_value(self._LINK_DESCRIPTION_KEY)

    @link_description.setter
    def link_description(self, value):
        self._set_prop_value(self._LINK_DESCRIPTION_KEY, value)

    @property
    def message(self):
        """Gets or sets the one time message for the service.

        :type: str
        """
        return self._get_prop_value(self._MESSAGE_KEY)

    @message.setter
    def message(self, value):
        self._set_prop_value(self._MESSAGE_KEY, value)

    @property
    def min_refresh_period(self):
        """Gets or sets the minimum refresh period for the service.

        The minimum refresh period is the time wherein repeated requests for refresh from a client will be ignored.

        :type: int
        """
        return self._get_prop_value(self._MIN_REFRESH_PERIOD_KEY)

    @min_refresh_period.setter
    def min_refresh_period(self, value):
        self._set_prop_value(
            self._MIN_REFRESH_PERIOD_KEY,
            self._editor.verify_int(value, "min. refresh period"))

    @property
    def use_default_snippets(self):
        """Gets or sets a value indicating whether or not to use default snippets.

        :type: bool
        """
        return self._get_prop_value(self._USE_DEFAULT_SNIPPETS_KEY)

    @use_default_snippets.setter
    def use_default_snippets(self, value):
        self._set_prop_value(self._USE_DEFAULT_SNIPPETS_KEY, self._editor.value_to_boolean(value))

    @property
    def use_network_link_control_tag(self):
        """Gets or sets a value indicating whether or not to use the NetworkLinkControl tag.

        NetworkLinkControl allows server side control of client data requests.

        :type: bool
        """
        return self._get_prop_value(self._USE_NETWORK_LINK_CONTROL_TAG_KEY)

    @use_network_link_control_tag.setter
    def use_network_link_control_tag(self, value):
        self._set_prop_value(self._USE_NETWORK_LINK_CONTROL_TAG_KEY, self._editor.value_to_boolean(value))