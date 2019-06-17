from ._dotnet import singlethreadapartment

# hide sys from * imports
import sys as _sys

if _sys.version_info[0] < 3:
    # running against ArcGIS Desktop
    from .arcobjects import *
else:
    # running against ArcGIS Pro
    from .arcgispro import *
