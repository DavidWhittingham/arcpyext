# coding=utf-8

# Python 2/3 compatibility
# pylint: disable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position,import-error,no-name-in-module
from __future__ import (absolute_import, division, print_function, unicode_literals)
from future.builtins.disabled import *
from future.builtins import *
from future.standard_library import install_aliases
install_aliases()
# pylint: enable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position,import-error,no-name-in-module


def read_file_in_zip(zip_file, file_path, decode="utf-8"):
    """Reads in an XML file as UTF-8 from a zip file."""
    with zip_file.open(file_path) as fp:
        if decode:
            return fp.read().decode(decode)
        else:
            return fp.read()


def passthrough_prop(prop_name, doc=None, obj_name="_cim_obj"):
    """Factory function for creating a property that passes through to the underlying ArcGIS Pro SDK object."""
    def _get(self):
        try:
            obj = getattr(self, obj_name)
            return getattr(obj, prop_name)
        except AttributeError as ae:
            raise AttributeError(
                "Unable to get the {} property on this instance of {}.".format(prop_name, self.__class__.__name__)
            )

    def _set(self, val):
        raise NotImplementedError("Property {} cannot be set".format(prop_name))

    def _del(self, val):
        raise NotImplementedError("Property {} cannot be deleted".format(prop_name))

    return property(_get, None, None, doc)