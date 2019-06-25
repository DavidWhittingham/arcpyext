# coding=utf-8
"""This module contains classes used in making map document/project comparisons."""

# Python 2/3 compatibility
# pylint: disable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position,import-error,no-name-in-module
from __future__ import (absolute_import, division, print_function, unicode_literals)
from future.builtins.disabled import *
from future.builtins import *
from future.standard_library import install_aliases
install_aliases()
from future.utils import iteritems
# pylint: enable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position,import-error,no-name-in-module

# Standard lib imports
import operator

# Local imports
from ._compare_helpers import *
from .._json import JsonEnum


class _ChangeTypesBase(JsonEnum):
    @classmethod
    def compare(cls, was_desc_part, now_desc_part):
        differences = []

        for change in cls:
            was_value = change.value.get_value(was_desc_part)
            now_value = change.value.get_value(now_desc_part)

            if change.value.test(was_value, now_value):
                differences.append(MapDocChange(change, was_value, now_value))
                if change.value.skip_remainder:
                    # skip all remaining tests
                    break

        return differences


class ChangeSeverity(JsonEnum):
    INFO = {"id": 0, "level": "Info"}
    WARNING = {"id": 1, "level": "Warning"}
    ERROR = {"id": 2, "level": "Error"}


class ChangeType(object):
    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def severity(self):
        return self._severity

    @property
    def skip_remainder(self):
        return self._skip_remainder

    def __init__(self, change_id, name, severity, get_value, test, skip_remainder=False):
        self._id = change_id
        self._name = name
        self._severity = severity
        self._skip_remainder = skip_remainder
        self.get_value = get_value
        self.test = test

    def get_value(self, obj):
        # implementation passed into init
        pass

    def test(self, was, now):
        # implementation passed into init
        pass

    def __iter__(self):
        return iteritems(self._to_jsonable())

    def _to_jsonable(self):
        return {"id": self.id, "severity": self.severity, "name": self.name}


class DocumentChangeTypes(_ChangeTypesBase):

    # Order is important for test evaluation (some tests skip the remaining tests), but declared order is not
    # respected on Python 2.x.  Explictly set order here to compensate.
    __order__ = " ".join(["MAP_COUNT_CHANGED"])

    MAP_COUNT_CHANGED = ChangeType(301, "Map Count Changed",
                                   ChangeSeverity.WARNING, lambda doc_desc: len(doc_desc["maps"]), operator.ne)


class LayerChangeTypes(_ChangeTypesBase):

    # Order is important for test evaluation (some tests skip the remaining tests), but declared order is not
    # respected on Python 2.x.  Explictly set order here to compensate.
    __order__ = " ".join([
        "LAYER_BROKEN", "LAYER_REMOVED", "LAYER_ID_NOT_SET", "LAYER_ADDED", "LAYER_NAME_CHANGED",
        "LAYER_DATASOURCE_CHANGED", "LAYER_VISIBILITY_CHANGED", "LAYER_ID_CHANGED", "LAYER_FIELDS_ADDED",
        "LAYER_FIELDS_REMOVED", "LAYER_DEFINITION_QUERY_CHANGED"
    ])

    LAYER_BROKEN = ChangeType(412,
                              "Layer: Broken",
                              ChangeSeverity.ERROR,
                              lambda layer_desc: layer_desc.get("isBroken") if not layer_desc is None else None,
                              lambda a, b: b is True,
                              skip_remainder=True)
    LAYER_REMOVED = ChangeType(411,
                               "Layer: Removed",
                               ChangeSeverity.ERROR,
                               lambda layer_desc: bool(layer_desc),
                               lambda a, b: a is True and b is False,
                               skip_remainder=True)
    LAYER_ID_NOT_SET = ChangeType(407,
                                  "Layer: Service ID Not Set",
                                  ChangeSeverity.ERROR,
                                  lambda layer_desc: layer_desc.get("serviceId") if not layer_desc is None else None,
                                  lambda a, b: b is None,
                                  skip_remainder=True)
    LAYER_ADDED = ChangeType(410,
                             "Layer: Added",
                             ChangeSeverity.INFO,
                             lambda layer_desc: bool(layer_desc),
                             lambda a, b: a is False and b is True,
                             skip_remainder=True)
    LAYER_NAME_CHANGED = ChangeType(402, "Layer: Name Changed",
                                    ChangeSeverity.WARNING, lambda layer_desc: layer_desc.get("name", ""), operator.ne)
    LAYER_DATASOURCE_CHANGED = ChangeType(403, "Layer: Datasource Changed",
                                          ChangeSeverity.WARNING, lambda layer_desc: get_datasource_info(
                                              layer_desc), lambda a, b: not dictionaries_eq_ignore_case(a, b))
    LAYER_VISIBILITY_CHANGED = ChangeType(404, "Layer: Visibility Changed",
                                          ChangeSeverity.WARNING, lambda layer_desc: layer_desc["visible"], operator.ne)

    LAYER_ID_CHANGED = ChangeType(401, "Layer: Service ID Changed",
                                  ChangeSeverity.ERROR, lambda layer_desc: layer_desc["serviceId"], operator.ne)
    LAYER_FIELDS_ADDED = ChangeType(
        408, "Layer: Fields Added",
        ChangeSeverity.INFO, lambda layer_desc: get_fields_compare_info(layer_desc["fields"] or []), lambda was_fields,
        now_fields: is_superset(now_fields, was_fields) and not is_superset(was_fields, now_fields))
    LAYER_FIELDS_REMOVED = ChangeType(
        409, "Layer: Fields Removed", ChangeSeverity.ERROR, lambda layer_desc: get_fields_compare_info(layer_desc[
            "fields"] or []), lambda was_fields, now_fields: not is_superset(now_fields, was_fields))
    LAYER_DEFINITION_QUERY_CHANGED = ChangeType(
        406, "Layer: Definition Query Changed",
        ChangeSeverity.WARNING, lambda layer_desc: layer_desc["definitionQuery"], operator.ne)


class MapChangeTypes(_ChangeTypesBase):

    # Order is important for test evaluation (some tests skip the remaining tests), but declared order is not
    # respected on Python 2.x.  Explictly set order here to compensate.
    __order__ = " ".join(["MAP_DELETED", "MAP_COOR_SYS_CHANGED"])

    MAP_DELETED = ChangeType(305,
                             "Map Deleted",
                             ChangeSeverity.ERROR,
                             lambda map_desc: bool(map_desc),
                             lambda a, b: a is True and b is False,
                             skip_remainder=True)
    MAP_COOR_SYS_CHANGED = ChangeType(
        302, "Map Coordinate System Changed",
        ChangeSeverity.ERROR, lambda map_desc: map_desc["spatialReference"].exportToString(), operator.ne)


class MapDocChange(object):
    @property
    def now(self):
        return self._now

    @property
    def type(self):
        return self._type

    @property
    def was(self):
        return self._was

    def __init__(self, change_type, was, now):
        self._type = change_type
        self._was = was
        self._now = now

    def __iter__(self):
        return iteritems(self._to_jsonable())

    def _to_jsonable(self):
        return {"type": self.type, "was": self.was, "now": self.now}
