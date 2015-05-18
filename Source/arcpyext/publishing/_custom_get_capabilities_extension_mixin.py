from __future__ import (absolute_import, division, print_function, unicode_literals)
from builtins import (ascii, bytes, chr, dict, filter, hex, input, int, map, next, oct, open, pow,
                      range, round, str, super, zip)

from ._sddraft_extension import SDDraftExtension


class CustomGetCapabilitiesExtensionMixin(SDDraftExtension):
    _CUSTOM_GET_CAPABILITIES_KEY = "customGetCapabilities"
    _PATH_TO_CUSTOM_GET_CAPABILITIES_FILES_KEY = "pathToCustomGetCapabilitiesFiles"

    @property
    def custom_get_capabilities(self):
        """Gets or sets a value indicating whether or not a custom get capabilities file is to be used.

        If set to true, the 'path_to_custom_get_capabilities_files' property must be set.

        :type: bool
        """
        return self._get_prop_value(self._CUSTOM_GET_CAPABILITIES_KEY)

    @custom_get_capabilities.setter
    def custom_get_capabilities(self, value):
        self._set_prop_value(self._CUSTOM_GET_CAPABILITIES_KEY, self._editor.value_to_boolean(value))

    @property
    def path_to_custom_get_capabilities_files(self):
        """Gets or sets the path to the custom get capabilities file(s).

        Path should be a URL with ending in a prefix for the capabilities files that have been
        created.  ArcGIS Server will then look files matching path with varying WMS versions
        appended.  For example, a 'Roads' service may have a custom path set as
        'http://www.myserver.com/ArcGIS/WMS/services/Roads' and ArcGIS Server will then look for
        'http://www.myserver.com/ArcGIS/WMS/services/Roads<version_number_here>.xml' (e.g.
        'http://www.myserver.com/ArcGIS/WMS/services/Roads1.0.0.xml').

        :type: str
        """
        return self._get_prop_value(self._PATH_TO_CUSTOM_GET_CAPABILITIES_FILES_KEY)

    @path_to_custom_get_capabilities_files.setter
    def path_to_custom_get_capabilities_files(self, value):
        self._set_prop_value(self._PATH_TO_CUSTOM_GET_CAPABILITIES_FILES_KEY, value)