"""arcpyext

Python Library that provides useful functions when working with the Esri ArcPy library.
"""

from ._version import *

# setup module logging with null handler
import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())

from ._patches import apply as _apply_patches
_apply_patches()

from . import _native
from . import _str
from . import conversion
from . import data
from . import mapping
from . import publishing
from . import schematransform
from . import toolbox
from ._utils import get_arcgis_version
from .TopicCategory import TopicCategory