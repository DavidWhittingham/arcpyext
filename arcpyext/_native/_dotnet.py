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

# Third-party imports
import clr

# .NET Imports
import System
import System.Threading

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
            latest_version_dir = os.path.join(simple_assembly_path, sorted(os.listdir(simple_assembly_path))[len_sorted_version_dirs-1])
            dll_path = os.path.join(latest_version_dir, simple_name + ".dll")
            if os.path.isfile(dll_path):
                return dll_path
    return None