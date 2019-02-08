# Python 2/3 compatibility
from __future__ import (absolute_import, division, print_function, unicode_literals)
from future.builtins import *
from future.builtins.disabled import *
from future.standard_library import install_aliases
install_aliases()

from ._sddraft_extension import SDDraftExtension

from enum import Enum


class MobileServerExtension(SDDraftExtension):

    _EXTENSION_TYPE = "MobileServer"

    @property
    def capabilities(self):
        """Gets or sets a list of capabilities (as defined by the self.Capabilities enumerator)
        that are enabled for this extension.

        :type: list(self.Capabilities)
        """
        return None

    @capabilities.setter
    def capabilities(self, values):
        raise NotImplementedError("No capabilities can be set for the Mobile Server Extension.")