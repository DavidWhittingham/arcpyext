# Python 2/3 compatibility
from __future__ import (absolute_import, division, print_function, unicode_literals)
from future.builtins import *
from future.builtins.disabled import *
from future.standard_library import install_aliases
install_aliases()

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