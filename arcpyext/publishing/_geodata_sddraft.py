from __future__ import (absolute_import, division, print_function, unicode_literals)
from builtins import (bytes, dict, int, list, object, range, str, ascii, chr, hex, input, next, oct, open, pow, round,
                      super, filter, map, zip)

from enum import Enum

from ._sddraft_base import SDDraftBase
from ._sddraft_max_record_count import SDDraftMaxRecordCountMixin
from ._sddraft_output_dir import SDDraftOutputDirMixin
from ._wcs_server_extension import WcsServerExtension
from ._wfs_server_extension import WfsServerExtension


class GeodataSDDraft(SDDraftMaxRecordCountMixin, SDDraftOutputDirMixin, SDDraftBase):

    class Capability(Enum):
        query = "Query"
        extraction = "Extraction"
        replication = "Replication"

    def __init__(self, editor):
        super(GeodataSDDraft, self).__init__(editor)
        self._wcs_server_extension = WcsServerExtension(editor)
        self._wfs_server_extension = WfsServerExtension(editor)

    @property
    def capabilities(self):
        """Gets a list of the enabled operations (by type name) that are currently enabled for the feature service."""
        # remove "Uploads" as is an internal operation and not exposed in the ArcMap/Server UI.
        return [self.Capability(item) for item in self._editor.get_element_value(self._capabilities_element).split(",")
            if item != "Uploads"]

    @capabilities.setter
    def capabilities(self, values):
        """Sets the operations (by an iterable of operation names) that are enabled for the feature service.

        :type: self.Capability
        """
        values = set([self._editor.enum_to_str(val, self.Capability, "capability") for val in values])
        if "Replication" in values:
            # If "Replication" is in the list of capabilities, the "Uploads" operation must also be enabled.
            # This functionality is hidden in the UI, but occurs when creating the service
            # definition draft in ArcMap.
            values.update(["Uploads"])

        if not "Query" in values:
            # ArcMap doesn't allow Query to be disabled for Geodata services.
            values.update(["Query"])

        self._editor.set_element_value(self._capabilities_element, ",".join(values))

    @property
    def wcs_server(self):
        """Gets the properties for the WCS Server extension."""
        return self._wcs_server_extension

    @property
    def wfs_server(self):
        """Gets the properties for the WFS Server extension."""
        return self._wfs_server_extension