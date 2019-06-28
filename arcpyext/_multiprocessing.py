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

import multiprocessing as _mp
import traceback as _tb

class Process(_mp.Process):
    """
    Extends multiprocessing.Process to catch exceptions thrown on the sub-process and make them available to the
    calling process.
    """

    def __init__(self, *args, **kwargs):
        _mp.Process.__init__(self, *args, **kwargs)
        self._pconn, self._cconn = _mp.Pipe()
        self._exception = None

    def run(self):
        try:
            _mp.Process.run(self)
            self._cconn.send(None)
        except Exception as e:
            tb = _tb.format_exc()
            self._cconn.send((e, tb))

    @property
    def exception(self):
        if self._pconn.poll():
            self._exception = self._pconn.recv()
        return self._exception