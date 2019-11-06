# coding=utf-8

# Python 2/3 compatibility
# pylint: disable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position,import-error,no-name-in-module
from __future__ import (absolute_import, division, print_function, unicode_literals)
from future.builtins.disabled import *
from future.builtins import *
from future.standard_library import install_aliases
install_aliases()
# pylint: enable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position,import-error,no-name-in-module

from .layers import ProFeatureLayer, ProGroupLayer, ProRasterLayer

def create_layer(proj_zip, layer_xml):
    """Factory function for creating a layer object bassed on the input XML."""
    # determine XML type
    layer_obj = None
    if layer_xml.startswith("<CIMFeatureLayer"):
        layer_obj = ProFeatureLayer(proj_zip, layer_xml)
    elif layer_xml.startswith("<CIMGroupLayer"):
        layer_obj = ProGroupLayer(proj_zip, layer_xml)
    elif layer_xml.startswith("<CIMRasterLayer"):
        layer_obj = ProRasterLayer(proj_zip, layer_xml)
    return layer_obj