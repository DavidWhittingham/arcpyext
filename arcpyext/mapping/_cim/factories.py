# coding=utf-8

# Python 2/3 compatibility
# pylint: disable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position,import-error,no-name-in-module
from __future__ import (absolute_import, division, print_function, unicode_literals)
from future.builtins.disabled import *
from future.builtins import *
from future.standard_library import install_aliases
install_aliases()
# pylint: enable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position,import-error,no-name-in-module

import json

from .layers import ProFeatureLayer, ProGroupLayer, ProRasterLayer


def create_layer(proj_zip, layer_string):
    """Factory function for creating a layer object bassed on the input string."""
    # determine layer type, try to pass as JSON first
    layer_obj = None

    if layer_string.startswith("{"):
        # layer is a JSON string, decode to determine type

        layer_json = json.loads(layer_string)
        layer_type = layer_json["type"]
        if layer_type == "CIMFeatureLayer":
            layer_obj = ProFeatureLayer(proj_zip, layer_string)
        elif layer_type == "CIMGroupLayer":
            layer_obj = ProGroupLayer(proj_zip, layer_string)
        elif layer_type == "CIMRasterLayer":
            layer_obj = ProRasterLayer(proj_zip, layer_string)
    else:
        # layer is probably XML, fallback to that
        if layer_string.startswith("<CIMFeatureLayer"):
            layer_obj = ProFeatureLayer(proj_zip, layer_string)
        elif layer_string.startswith("<CIMGroupLayer"):
            layer_obj = ProGroupLayer(proj_zip, layer_string)
        elif layer_string.startswith("<CIMRasterLayer"):
            layer_obj = ProRasterLayer(proj_zip, layer_string)

    return layer_obj