# coding=utf-8
"""
This module contains patches to Esri's *arcpy._mp.Map* class.  These patches may insert functionality or fix issues
directly in the *arcpy._mp.Map* class.
"""

import arcpy

from arcpy._mp import Layer, Map

from ..._str.utils import caseless_equal
from ._cim_helpers import get_cim_version


def add_set_layer_visibility():
    def set_layer_visibility(self, layer_visibility):
        # type: (Map, str) -> None
        """Set layer visibility based on a string description.

        Args:
            layer_visibility (str): A description of the layer visibility to apply, in the same format as the MapServer ExportMap layers specification.

        Raises:
            ValueError: Raised in the event the layer visibility input can not be parsed or is otherwised unrecognized.
        """

        if not layer_visibility:
            raise ValueError("Layer visibility cannot be None.")

        try:
            (layers_op, layers_list) = [s.strip() for s in layer_visibility.split(":")]
            layers_list = [id.strip() for id in layers_list.split(",")]
        except:
            raise ValueError("Could not parse layers list to determine layer visiblity: %s", layer_visibility)

        for layer in self.listLayers():
            layer = layer  #type: Layer
            layer_id = str(layer.getDefinition(get_cim_version()).serviceLayerID)

            if caseless_equal(layers_op, "show"):
                # make only the specified layers visible
                if layer_id in layers_list:
                    layer.visible = True
                else:
                    layer.visible = False
            elif caseless_equal(layers_op, "hide"):
                # make all layers visible except those specified
                if layer_id in layers_list:
                    layer.visible = False
                else:
                    layer.visible = True
            elif caseless_equal(layers_op, "include"):
                # make the specified layers visible, along with the defaults
                if layer_id in layers_list:
                    layer.visible = True
            elif caseless_equal(layers_op, "exclude"):
                # make the specified layers invisible, along with the defaults
                if layer_id in layers_list:
                    layer.visible = False
            else:
                raise ValueError("Layer visibility operation not recognized.")

    arcpy._mp.Map.setLayerVisibility = set_layer_visibility


add_set_layer_visibility()
