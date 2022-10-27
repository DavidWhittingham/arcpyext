# coding=utf-8
"""
This module contains functionality for interacting with the CLR.
"""

# Python 2/3 compatibility
# pylint: disable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position
from __future__ import (absolute_import, division, print_function, unicode_literals)
from future.builtins.disabled import *
from future.builtins import *
from future.standard_library import install_aliases
install_aliases()
# pylint: enable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position

# Standard lib imports
import os
import re
import sys

from decimal import Decimal

# Third-party imports
import arcpy

# clr import, must work out whether we are .NET 6 and setup coreclr first
if sys.version_info[0] >= 3:
    arcpy_install_info = arcpy.GetInstallInfo()
    major_version = Decimal(re.search(r"^(\d+\.\d+)", arcpy.GetInstallInfo()['Version'], re.IGNORECASE).group(1))
    from clr_loader import get_coreclr
    from pythonnet import set_runtime

    if arcpy_install_info["ProductName"] == "Server" and major_version >= Decimal(11.0):
        # running against server, on Python 3, on version 11 or greater
        dotnet_config = os.path.join(arcpy_install_info["InstallDir"], r"bin\ArcSOC.runtimeconfig.json")
        rt = get_coreclr(runtime_config=dotnet_config)
        set_runtime(rt)
    elif major_version >= Decimal(3.0):
        # if we're not on server, and the product version is 3 or greater (assume pro)
        dotnet_config = os.path.join(arcpy_install_info["InstallDir"], r"bin\ArcGISPro.runtimeconfig.json")
        rt = get_coreclr(runtime_config=dotnet_config)
        set_runtime(rt)

import clr

# .NET Imports
import System
import System.Threading
import System.Runtime.InteropServices


class ComReleaser(object):
    """Python/PythonNet implementation similar to the ComReleaser object in ArcObjects."""

    _com_objects = None

    def __init__(self):
        self._com_objects = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if not self._com_objects:
            # not initialised or empty
            return

        for obj in self._com_objects:
            self.release_com_object(obj)

        self._com_objects = None

    def manage_lifetime(self, obj):
        self._com_objects.append(obj)

    def release_com_object(self, obj):
        if obj is None:
            # skip if None
            return

        if not isinstance(obj, System.Object):
            # skip if the object didn't come from .NET
            return

        if not System.Runtime.InteropServices.Marshal.IsComObject(obj):
            # skip if not a COM object
            return

        # obj isn't null and is a COM object, loop the release until no refs held
        while System.Runtime.InteropServices.Marshal.ReleaseComObject(obj) > 0:
            # doing is done in the while loop test, do nothing here
            pass


def singlethreadapartment(func=None):
    def decorator(func):
        """Factory for creating the STA decorator."""
        def sta_wrapper(*args, **kwargs):
            """The STA wrapper function."""

            # Create an 'outer' result value
            result = {}

            def thread_exec():
                """The function passed to .NET, cannot contain arguments or return values."""
                # Assign the result outside the execution of this function
                result["result"] = func(*args, **kwargs)

            # Create a new thread, with the thread_exec method as the code runner
            thread = System.Threading.Thread(System.Threading.ThreadStart(thread_exec))

            # Set thread to Single Thread Apartment mode, for accessing COM safely
            thread.SetApartmentState(System.Threading.ApartmentState.STA)

            # Start the thread, join and wait for conclusion of work
            thread.Start()
            thread.Join()

            # return the result that has been placed outside the thread_exec function
            return result["result"]

        return sta_wrapper

    if func is None:
        # if decorator is called parameterlessly
        return decorator
    else:
        # execute the factory given the passed-in function
        return decorator(func)


def find_gac_assembly_path(simple_name):
    gac_path = os.path.join(os.environ["windir"], "Microsoft.NET\\assembly\\GAC_MSIL")
    simple_assembly_path = os.path.join(gac_path, simple_name)
    if os.path.isdir(simple_assembly_path):
        # some version of the assembly seems to exist
        sorted_version_dirs = sorted(os.listdir(simple_assembly_path))
        len_sorted_version_dirs = len(sorted_version_dirs)
        if len_sorted_version_dirs > 0:
            latest_version_dir = os.path.join(
                simple_assembly_path,
                sorted(os.listdir(simple_assembly_path))[len_sorted_version_dirs - 1]
            )
            dll_path = os.path.join(latest_version_dir, simple_name + ".dll")
            if os.path.isfile(dll_path):
                return dll_path
    return None