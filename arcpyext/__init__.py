"""arcpyext

Python Library that provides useful functions when working with the Esri ArcPy library.
"""

from ._version import *

# setup module logging with null handler
import logging
logging.getLogger("arcpyext").addHandler(logging.NullHandler())

import arcpy
from . import _patches as _patches
_patches.apply()

from . import conversion
from . import data
from . import publishing
from . import toolbox
from . import schematransform
from . import arcobjects

# import arcpy version-specific mapping modules
try:
    import arcpy.mapping
    from . import mapping
except (AttributeError, ImportError):
    from . import mp