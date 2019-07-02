# Set the apartment state for talking to COM
import ctypes as _ctypes
_ctypes.windll.ole32.CoInitializeEx(0, 2)

from ._dotnet import singlethreadapartment, ComReleaser

# hide sys from * imports
import sys as _sys

if _sys.version_info[0] < 3:
    # running against ArcGIS Desktop
    from .arcobjects import *
else:
    # running against ArcGIS Pro
    from .arcgispro import *
