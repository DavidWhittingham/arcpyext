# coding=utf-8
"""
This module handles applying patches to Esri's *arcpy* module.  These patches may insert functionality or fix issues
directly in the *arcpy* module.
"""

# Python 2/3 compatibility
# pylint: disable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position
from __future__ import (absolute_import, division, print_function, unicode_literals)
from future.builtins.disabled import *
from future.builtins import *
from future.standard_library import install_aliases
install_aliases()
# pylint: enable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position

import arcpy
import re

from decimal import Decimal


def apply():
    """
    Applies all the patches contained is this module.
    """

    fix_mapping_versions()


def fix_mapping_versions():
    """
    This function monkey patches the mapping version information in arcpy to support the currently installed version,
    along with past versions if they are not included (arcpy 10.5 does not have 10.4 supported version, but the
    support is there under the hood).
    """

    # get ArcGIS version as a number
    ags_version = Decimal(
        re.search(r"^(\d+\.\d+)",
                  arcpy.GetInstallInfo()['Version'], re.IGNORECASE).group(1))

    # surrounded in try/pass to fail gracefully in case Esri change the design of this internal API
    try:
        versions = arcpy._mapping.constants.__args__["version"]

        if ags_version >= Decimal("10.4") and "10.4" not in versions:
            versions["10.4"] = 104

        if ags_version >= Decimal("10.5") and "10.5" not in versions:
            versions["10.5"] = 105

        if ags_version >= Decimal("10.6") and "10.6" not in versions:
            versions["10.6"] = 106
    except:
        pass