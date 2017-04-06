from __future__ import (absolute_import, division, print_function, unicode_literals)
from builtins import (ascii, bytes, chr, dict, filter, hex, input, int, map, next, oct, open, pow,
                      range, round, str, super, zip)

from ._sddraft_extension import SDDraftExtension


class JpipServerExtension(SDDraftExtension):

    _EXTENSION_TYPE = "JPIPServer"

    @property
    def capabilities(self):
        """JPIP Server Extension does not support capabilities.  Returns None, raises NotImplementedError on set."""
        return None

    @capabilities.setter
    def capabilities(self, values):
        raise NotImplementedError("No capabilities can be set for the JPIP Server Extension.")