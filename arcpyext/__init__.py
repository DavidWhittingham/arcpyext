"""arcpyext

Python Library that provides useful functions when working with the Esri ArcPy library.
"""

from ._version import *

# setup module logging with null handler
import logging
logging.basicConfig(filename="./logfile.log")
logging.getLogger("arcpyext").addHandler(logging.NullHandler())

import arcpy
from . import _patches as _patches
_patches.apply()

from . import _native
from . import conversion
from . import data
from . import toolbox
from . import schematransform
from . import mapping
from . import publishing

try:
    # Python 2 imports
    import arcpy.mapping
except (AttributeError, ImportError):
    # Python 3 imports
    pass
