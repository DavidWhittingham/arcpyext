# coding=utf-8

# Python 2/3 compatibility
# pylint: disable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position,import-error,no-name-in-module
from __future__ import (absolute_import, division, print_function, unicode_literals)
from future.builtins.disabled import *
from future.builtins import *
from future.standard_library import install_aliases

install_aliases()
from future.moves.collections import deque
from future.utils import with_metaclass
# pylint: enable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position,import-error,no-name-in-module

# Standard lib imports
from abc import ABCMeta

# Local imports
from .helpers import passthrough_prop
from .tables import ProFeatureTable

# .NET Imports
from ArcGIS.Core.CIM import CIMFeatureLayer, CIMGroupLayer, CIMRasterLayer, CIMMosaicLayer, CIMImageMosaicSubLayer, CIMFeatureMosaicSubLayer


class ProLayerBase(with_metaclass(ABCMeta, object)):

    _children = None
    _cim_obj = None
    _long_name = None
    _parent = None
    _proj_zip = None

    def __init__(self, proj_zip, cim_obj):
        self._children = []
        self._proj_zip = proj_zip
        self._cim_obj = cim_obj

    description = passthrough_prop("Description")
    name = passthrough_prop("Name")
    service_id = passthrough_prop("ServiceLayerID")
    visible = passthrough_prop("Visibility")

    @property
    def children(self):
        return self._children.copy()

    @property
    def parent(self):
        return self._parent

    @property
    def long_name(self):
        name_parts = deque()

        def build_layer_name(layer):
            # add to name parts
            name_parts.appendleft(layer.name)

            if layer.parent:
                build_layer_name(layer.parent)

        build_layer_name(self)

        return "\\".join(name_parts)

    def _get_child_paths(self):
        return []


class ProBasicFeatureLayer(ProLayerBase):

    _feature_table = None

    def __init__(self, proj_zip, cim_obj):
        super().__init__(proj_zip, cim_obj)

    @property
    def feature_table(self):
        if not self._feature_table:
            self._feature_table = ProFeatureTable(self._cim_obj.FeatureTable)

        return self._feature_table


class ProFeatureLayer(ProBasicFeatureLayer):
    def __init__(self, proj_zip, layer_string):
        try:
            super().__init__(proj_zip, CIMFeatureLayer.FromXml(layer_string))
        except AttributeError:
            # probably JSON, attempt that
            super().__init__(proj_zip, CIMFeatureLayer.FromJson(layer_string))


class ProRasterLayer(ProLayerBase):
    def __init__(self, proj_zip, layer_string):
        try:
            super().__init__(proj_zip, CIMRasterLayer.FromXml(layer_string))
        except AttributeError:
            # probably JSON, attempt that
            super().__init__(proj_zip, CIMRasterLayer.FromJson(layer_string))


class ProGroupLayer(ProLayerBase):
    def __init__(self, proj_zip, layer_string):
        try:
            super().__init__(proj_zip, CIMGroupLayer.FromXml(layer_string))
        except AttributeError:
            # probably JSON, attempt that
            super().__init__(proj_zip, CIMGroupLayer.FromJson(layer_string))

    def _get_child_paths(self):
        # Layers can be a none if the group layer is empty, so guard against that
        return [cp[8:] for cp in self._cim_obj.Layers or []]


class ProMosaicLayer(ProLayerBase):
    def __init__(self, proj_zip, layer_string):
        try:
            super().__init__(proj_zip, CIMMosaicLayer.FromXml(layer_string))
        except AttributeError:
            # probably JSON, attempt that
            super().__init__(proj_zip, CIMMosaicLayer.FromJson(layer_string))

    def _get_child_paths(self):
        return [self._cim_obj.BoundaryLayer[8:], self._cim_obj.FootprintLayer[8:], self._cim_obj.ImageLayer[8:]]


class ProFeatureMosaicSubLayer(ProLayerBase):
    def __init__(self, proj_zip, layer_string):
        try:
            super().__init__(proj_zip, CIMFeatureMosaicSubLayer.FromXml(layer_string))
        except AttributeError:
            # probably JSON, attempt that
            super().__init__(proj_zip, CIMFeatureMosaicSubLayer.FromJson(layer_string))


class ProImageMosaicSubLayer(ProLayerBase):
    def __init__(self, proj_zip, layer_string):
        try:
            super().__init__(proj_zip, CIMImageMosaicSubLayer.FromXml(layer_string))
        except AttributeError:
            # probably JSON, attempt that
            super().__init__(proj_zip, CIMImageMosaicSubLayer.FromJson(layer_string))
