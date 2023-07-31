# coding=utf-8

# Python 2/3 compatibility
# pylint: disable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position,import-error,no-name-in-module
from __future__ import (absolute_import, division, print_function, unicode_literals)
from future.builtins.disabled import *
from future.builtins import *
from future.standard_library import install_aliases
from future.utils import raise_from
install_aliases()
# pylint: enable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position,import-error,no-name-in-module


def read_file_in_zip(zip_file_obj, inner_file_path, decode="utf-8"):
    """Reads in an XML file as UTF-8 from a zip file."""
    with zip_file_obj.open(inner_file_path) as zip_file_handle:
        if decode:
            return zip_file_handle.read().decode(decode)

        return zip_file_handle.read()


def passthrough_prop(prop_name, doc=None, obj_name="_cim_obj"):
    """Factory function for creating a property that passes through to the underlying ArcGIS Pro SDK object."""
    def _get(self):
        try:
            obj = getattr(self, obj_name)
            return getattr(obj, prop_name)
        except AttributeError as attr_err:
            raise_from(
                AttributeError(
                    "Unable to get the {} property on this instance of {}.".format(prop_name, self.__class__.__name__)
                ), attr_err
            )

    return property(_get, None, None, doc)