# coding=utf-8
"""
This module contains functionality for accessing ArcObjects from Python

Based on code from here: http://www.pierssen.com/arcgis10/python.htm
"""

# Python 2/3 compatibility
# pylint: disable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position
from __future__ import (absolute_import, division, print_function, unicode_literals)
from future.builtins.disabled import *
from future.builtins import *
from future.standard_library import install_aliases
install_aliases()
# pylint: enable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position

# Third-party imports
import clr

from contextlib import contextmanager

# .NET Imports
clr.AddReference("ArcGIS.Core")
import System
import System.Threading
import ArcGIS.Core

def singlethreadapartment(func=None):
    def decorator(func):
        """Factory for creating the STA decorator."""

        def sta_wrapper(*args, **kwargs):
            """The STA wrapper function."""

            # Create an 'outer' result value
            result = None

            def thread_exec():
                """The function passed to .NET, cannot contain arguments or return values."""
                # Get access to the result value, outside this score
                nonlocal result

                # Assign the result outside the execution of this function
                result = func(*args, **kwargs)

            # Create a new thread, with the thread_exec method as the code runner
            thread = System.Threading.Thread(System.Threading.ThreadStart(thread_exec))

            # Set thread to Single Thread Apartment mode, for accessing COM safely
            thread.SetApartmentState(System.Threading.ApartmentState.STA)

            # Start the thread, join and wait for conclusion of work
            thread.Start()
            thread.Join()

            # return the result that has been placed outside the thread_exec function
            return result

        return sta_wrapper
    
    if func is None:
        # if decorator is called parameterlessly
        return decorator
    else:
        # execute the factory given the passed-in function
        return decorator(func)

@contextmanager
def licenced_context():
    # it appears arcpy being imported is enough to be licenced
    import arcpy
    try:
        yield
    finally:
        # no teardown required
        pass
