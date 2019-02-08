# Python 2/3 compatibility
from __future__ import (absolute_import, division, print_function, unicode_literals)
from future.builtins import *
from future.builtins.disabled import *
from future.standard_library import install_aliases
install_aliases()

class ArcPyExtError(Exception):
    """Base error class for all ArcPyExt errors."""
    
    def __init__(self, message, innerError = None):
        super(ArcPyExtError, self).__init__(message)
        self._innerError = innerError
       
    @property
    def innerError(self):
        return self._innerError