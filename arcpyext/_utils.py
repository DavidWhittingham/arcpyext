# coding=utf-8
"""This module contains helpers for dealing with multiprocessing."""

# Python 2/3 compatibility
# pylint: disable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position,no-name-in-module
from __future__ import (absolute_import, division, print_function, unicode_literals)
from future.builtins.disabled import *
from future.builtins import *
from future.standard_library import install_aliases
install_aliases()
# pylint: enable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position,no-name-in-module

# standard lib
import re

from decimal import Decimal

# third-party lib
import arcpy


def get_arcgis_version():
    return Decimal(re.search(r"^(\d+\.\d+)", arcpy.GetInstallInfo()['Version'], re.IGNORECASE).group(1))