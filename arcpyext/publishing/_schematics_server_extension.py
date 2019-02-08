# Python 2/3 compatibility
from __future__ import (absolute_import, division, print_function, unicode_literals)
from future.builtins import *
from future.builtins.disabled import *
from future.standard_library import install_aliases
install_aliases()

from ._sddraft_extension import SDDraftExtension

from enum import Enum


class SchematicsServerExtension(SDDraftExtension):

    class Capability(Enum):
        query = "Query"
        editing = "Editing"

    _EXTENSION_TYPE = "SchematicsServer"