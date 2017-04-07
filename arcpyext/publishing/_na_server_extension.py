from __future__ import (absolute_import, division, print_function, unicode_literals)
from builtins import (ascii, bytes, chr, dict, filter, hex, input, int, map, next, oct, open, pow,
                      range, round, str, super, zip)

from ._sddraft_extension import SDDraftExtension

from enum import Enum


class NaServerExtension(SDDraftExtension):

    _EXTENSION_TYPE = "NAServer"

    @property
    def capabilities(self):
        """No capabilities are supported for NaServerExtension. Returns None."""
        return None

    @capabilities.setter
    def capabilities(self, values):
        raise NotImplementedError("No capabilities can be set for the Network Analysis Server Extension.")