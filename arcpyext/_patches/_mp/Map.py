# coding=utf-8
"""
This module contains patches to Esri's *arcpy._mp.Map* class.  These patches may insert functionality or fix issues
directly in the *arcpy._mp.Map* class.
"""

import sys
import arcpy
from arcpy._mp import Layer, Map
from arcpyext._patches.patches import get_cim_version

from arcpyext._str.utils import caseless_equal


def add_set_layer_visibility():
    def set_layer_visibility(self, layer_visibility):
        # type: (Map, str) -> Map

        # process the layer visiblity string (same as Map Service ExportMap specification)
        try:
            (layers_op, layers_list) = [s.strip() for s in layer_visibility.split(":")]
            layers_list = [id.strip() for id in layers_list.split(",")]
        except:
            raise Exception("Could not parse layers list to determine layer visiblity: %s", layer_visibility)
        
        
        def set_layer_visibility_2():
            from arcpyext.mapping import _mapping2 as _mh
            # self is a ao_map_document
            for map_frame in _mh._native_list_maps(self):
                layer_list = _mh._native_list_layers(self, map_frame)
                
                for index, layer in enumerate(layer_list):
                    layer_desc = _mh._native_describe_layer(layer)
                    layer_id = str(layer_desc["serviceId"])

                    if caseless_equal(layers_op, "show"):
                        # make only the specified layers visible
                        if layer_id in layers_list:
                            layer_list[index]["layer"].Visible = True
                        else:
                            layer_list[index]["layer"].Visible = False
                    elif caseless_equal(layers_op, "hide"):
                        # make all layers visible except those specified
                        if layer_id in layers_list:
                            layer_list[index]["layer"].Visible = False
                        else:
                            layer_list[index]["layer"].Visible = True
                    elif caseless_equal(layers_op, "include"):
                        # make the specified layers visible, along with the defaults
                        if layer_id in layers_list:
                            layer_list[index]["layer"].Visible = True
                    elif caseless_equal(layers_op, "exclude"):
                        # make the specified layers invisible, along with the defaults
                        if layer_id in layers_list:
                            layer_list[index]["layer"].Visible = False
                    else:
                        raise ValueError("Layer visibility operation not recognized.")

        
        def set_layer_visibility_3():
            for layer in self.listLayers():
                layer = layer  # type: Layer
                cim_version = get_cim_version()
                layer_id = str(layer.getDefinition(cim_version).serviceLayerID)

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
        
        
        ARCPY_2 = sys.version_info[0] < 3
        if ARCPY_2:
            set_layer_visibility_2()
        else:
            set_layer_visibility_3()

        return self

    arcpy._mp.Map.set_layer_visibility = set_layer_visibility

add_set_layer_visibility()
