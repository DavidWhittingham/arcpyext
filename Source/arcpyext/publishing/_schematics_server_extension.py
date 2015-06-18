from __future__ import (absolute_import, division, print_function, unicode_literals)
from builtins import (ascii, bytes, chr, dict, filter, hex, input, int, map, next, oct, open, pow,
                      range, round, str, super, zip)

from ._sddraft_extension import SDDraftExtension

from enum import Enum


class SchematicsServerExtension(SDDraftExtension):

    class Capability(Enum):
        query = "Query"
        editing = "Editing"

    _EXTENSION_TYPE = "SchematicsServer"