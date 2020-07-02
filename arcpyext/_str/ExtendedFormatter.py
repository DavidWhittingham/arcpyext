# coding=utf-8
"""This module contains an extended string formatting class."""

# Python 2/3 compatibility
# pylint: disable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position,import-error,no-name-in-module
from __future__ import (absolute_import, division, print_function, unicode_literals)
from future.builtins.disabled import *
from future.builtins import *
from future.standard_library import install_aliases
install_aliases()
# pylint: enable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position,import-error,no-name-in-module

# Standard lib imports
from string import Formatter


class ExtendedFormatter(Formatter):
    """An extended format string formatter with custom symbols."""
    def format_field(self, value, format_spec):
        if isinstance(value, str):
            # add custom upper/lower case format specifier types
            if format_spec.endswith('u'):
                value = value.upper()
                format_spec = format_spec[:-1]
            elif format_spec.endswith('l'):
                value = value.lower()
                format_spec = format_spec[:-1]

            if not format_spec:
                return value

        return super().format_field(value, format_spec)
