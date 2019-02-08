# Python 2/3 compatibility
from __future__ import (absolute_import, division, print_function, unicode_literals)
from future.builtins import *
from future.builtins.disabled import *
from future.standard_library import install_aliases
install_aliases()

from .arc_py_ext_error import ArcPyExtError

class MapLayerError(ArcPyExtError):
    """ArcPyExt exception for errors involving map layers."""

    def __init__(self, message, layer, innerError = None):
        super(MapLayerError, self).__init__(message, innerError)
        self._layer = layer
        
    @property
    def layer(self):
        return self._layer