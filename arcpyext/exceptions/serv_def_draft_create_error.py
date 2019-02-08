# Python 2/3 compatibility
from __future__ import (absolute_import, division, print_function, unicode_literals)
from future.builtins import *
from future.builtins.disabled import *
from future.standard_library import install_aliases
install_aliases()

from .arc_py_ext_error import ArcPyExtError

class ServDefDraftCreateError(ArcPyExtError):
    """description of class"""