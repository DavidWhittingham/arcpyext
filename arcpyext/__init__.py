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

from . import conversion
from . import data
from . import toolbox
from . import schematransform

# import arcpy version-specific mapping modules
try:
    # py2 arcpy desktop
    import arcpy.mapping
    from .mapping import *
    from .mapping import _open_map_document as open_map_document
    from . import publishing
    from . import arcobjects

except (AttributeError, ImportError):
    # py3 arcpy pro
    from .mp import *
    from .publishing import convert_map_to_service_draft, load_image_sddraft

