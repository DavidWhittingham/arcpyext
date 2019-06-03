# coding=utf-8
"""This module contains shared functionality for mapping-related functions across arcpy versions."""

# Python 2/3 compatibility
# pylint: disable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position
from __future__ import (absolute_import, division, print_function, unicode_literals)
from future.builtins.disabled import *
from future.builtins import *
from future.standard_library import install_aliases
install_aliases()
from future.moves.collections import Mapping
from future.moves.itertools import chain, zip_longest
from future.utils import iteritems
# pylint: enable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position

# Standard libary imports
import json
import re
import sys

from enum import Enum  # comes from third-party package on Py 2

# Local imports
from ._compare_helpers import lowercase_dict
from .compare_types import *
from .._json import JsonEnum
from ..exceptions import MapLayerError, ChangeDataSourcesError

# Python-version dependent imports
ARCPY_2 = sys.version_info[0] < 3
if ARCPY_2:
    # import to get access to 'private' helper methds
    from . import _mapping2 as _mh

    # import all 'public' methods into current namespace
    from ._mapping2 import *
else:
    # import to get access to 'private' helper methds
    from . import _mapping3 as _mh

    # import all 'public' methods into current namespace
    from ._mapping3 import *


def change_data_sources(mxd_or_proj, data_sources):

    # make sure the MXD/project is open and not a path
    map_document = open_document(mxd_or_proj)

    errors = []

    # match map with data sources
    for map_frame, map_data_sources in zip_longest(_mh._list_maps(map_document), data_sources):

        if not 'layers' in map_data_sources or not 'tables' in map_data_sources:
            raise ChangeDataSourcesError("Data sources dictionary does not contain both layers and tables keys")

        layers = _mh._list_layers(map_document, map_frame)
        layer_sources = map_data_sources["layers"]

        if layer_sources == None or len(layers) != len(layer_sources):
            raise ChangeDataSourcesError("Number of layers does not match number of data sources.")

        for layer, layer_source in zip_longest(layers, layer_sources):
            try:
                if layer_source == None:
                    continue

                logger.debug("Layer {0}: Attempting to change workspace path".format(layer.longName))
                logger.debug("Current data source details: {0}".format(_mh._get_data_source_desc(layer)))
                _mh._change_data_source(layer, layer_source)
                logger.debug("Layer {0}: data source updated to: {1}".format(layer.name, layer_source))

            #TODO: Handle KeyError and AttributeError for badly written configs
            except MapLayerError as e:
                errors.append(e)

        data_tables = _mh._list_tables(map_document, map_frame)
        data_table_sources = map_data_sources["tables"]

        if not len(data_tables) == len(data_table_sources):
            raise ChangeDataSourcesError("Number of data tables does not match number of data table data sources.")

        for data_table, data_table_source in zip_longest(data_tables, data_table_sources):
            try:
                if data_table_source == None:
                    continue

                logger.debug("Data Table {0}: Attempting to change workspace path".format(data_table.name))
                logger.debug("Current data source details: {0}".format(_mh._get_data_source_desc(data_table)))
                _mh._change_data_source(data_table, data_table_source)
                logger.debug("Data Table {0}: Workspace path updated to: {1}".format(
                    data_table.name, data_table_source))

            except MapLayerError as mle:
                errors.append(mle)

    if not len(errors) == 0:
        raise ChangeDataSourcesError("A number of errors were encountered whilst change layer data sources.", errors)


def compare(was_mxd_proj_or_desc, now_mxd_proj_or_desc):

    was_description = was_mxd_proj_or_desc if isinstance(was_mxd_proj_or_desc,
                                                         Mapping) else describe(was_mxd_proj_or_desc)
    now_description = now_mxd_proj_or_desc if isinstance(now_mxd_proj_or_desc,
                                                         Mapping) else describe(now_mxd_proj_or_desc)

    #yapf: disable
    differences = {
        "document": DocumentChangeTypes.compare(was_description, now_description),
        "maps": [
            _compare_map_frames(was_frame, now_frame)
            for was_frame, now_frame in zip_longest(was_description["maps"], now_description["maps"])
        ]
    }
    #yapf: enable

    return differences


def create_replacement_data_sources_list(mxd_proj_or_desc,
                                         data_source_templates,
                                         raise_exception_no_change=False):

    def tokenise_table_name(x):
        """Given a feature class or feature dataset name, returns the schema (optional) and simple name"""

        if "." in x:
            return {"schema": x[:x.index(".")], "name": x[x.index(".") + 1:]}
        else:
            return {"schema": None, "name": x}

    def tokenise_datasource(x):
        """Given a fully qualified feature class path, returns the feature class' schema, simple name and parent dataset (optional)"""

        regex = r"([\w\.]+)?(/|\\+)([\w\.]+$)"
        parts = re.search(regex, x, re.MULTILINE | re.IGNORECASE)

        if parts and parts.groups > 3:

            dataset = None if ".gdb" in parts.group(1).lower() or ".sde" in parts.group(
                1).lower() else tokenise_table_name(parts.group(1))
            table = tokenise_table_name(parts.group(3))

            return {
                "schema": None if table["schema"] is None else table["schema"],
                "dataSet": None if dataset is None else dataset["name"],
                "table": table["name"]
            }

        else:
            return None

    # ensure we have a description of the map, and not a map itself
    map_desc = mxd_proj_or_desc if isinstance(mxd_proj_or_desc, Mapping) else describe(mxd_proj_or_desc)

    # Here we are rearranging the data_source_templates so that the match criteria can be compared as a set - in case there are more than one.
    #yapf: disable
    template_sets = [
        dict(
            list(iteritems(template)) + [
                ("matchCriteria", set(iteritems(lowercase_dict(template["matchCriteria"]))))
            ]
        ) for template in data_source_templates
    ]
    #yapf: enable

    # freeze values in dict for set comparison
    def freeze(d):
        """Freezes dicts and lists for set comparison."""
        if isinstance(d, dict):
            return frozenset((key, freeze(value)) for key, value in d.items())
        elif isinstance(d, list):
            return tuple(freeze(value) for value in d)
        return d

    def match_new_data_source(layer_or_table):
        if layer_or_table == None:
            return None

        new_conn = None
        for template in template_sets:
            # The layer_or_table variable contains properties that can't be put into sets without freezing
            if template["matchCriteria"].issubset(set(freeze(layer_or_table))):
                new_conn = template["dataSource"].copy()

                # Test #2: If the target workspace is a collection of workspaces, infer the target child workspace by using a
                # deterministic naming convention that maps the layer's dataset name to a workspace.
                if template.get("matchOptions", {}).get("isWorkspaceContainer") == True:

                    logger.debug("Data source template is workspace container.")

                    tokens = tokenise_datasource(layer_or_table["dataSource"])

                    if tokens is not None:

                        logger.debug("Tokens are: %s", tokens)

                        if tokens["dataSet"] is not None and tokens["schema"] is not None:
                            logger.debug(1.11)
                            new_conn["workspacePath"] = "{}\\{}.{}.gdb".format(new_conn["workspacePath"],
                                                                               tokens["schema"], tokens["dataSet"])
                        elif tokens["dataSet"] is not None:
                            logger.debug(1.12)
                            new_conn["workspacePath"] = "{}\\{}.gdb".format(new_conn["workspacePath"],
                                                                            tokens["dataSet"])
                        else:
                            logger.debug(1.13)
                            new_conn["workspacePath"] = "{}\\{}.gdb".format(new_conn["workspacePath"], tokens["table"])

                break
        if new_conn == None and raise_exception_no_change:
            raise RuntimeError("No matching data source was found for layer")
        return new_conn

    return [
        {
            "layers": [match_new_data_source(layer) for layer in df["layers"]],
            "tables": [match_new_data_source(table) for table in df["tables"]]
        } for df in map_desc["maps"]
    ]


def describe(mxd_or_proj):
    """Describe a Map Document or ArcGIS Pro project."""

    # Ensure document is open before
    mxd_or_proj = open_document(mxd_or_proj)

    mxd_or_proj = None
    try:

        # open the MXD in ArcObjects
        mxd_or_proj = _mh._native_document_open(mxd_or_proj.filePath)

        # build return object
        desc = {
            "maps": [_mh._native_describe_map(mxd_or_proj, map_frame) for map_frame in _mh._native_list_maps(mxd_or_proj)]
        }

    finally:
        if mxd_or_proj:
            # close the native document
            _mh._native_document_close(mxd_or_proj)

    return desc


def is_valid(mxd_or_proj):
    """Analyse the map for broken layers and return a boolean indicating if it is in a valid state or not.

    Lists broken layers on the shell output.

    :param map: The map to be validated
    :type map: arcpy.mapping.MapDocument
    :returns: Boolean, True if valid, False if there are one or more broken layers

    """

    description = describe(mxd_or_proj)

    broken_layers = []

    for m in description["maps"]:
        # iterate layers and tables
        for l in chain(m["layers"], m["tables"]):
            if l["isBroken"]:
                broken_layers.append(l)

    if len(broken_layers) > 0:
        #logger.debug(u"Map '{0}': Broken data sources:".format(description.title))
        for layer in broken_layers:
            logger.debug(u" {0}".format(layer["longName"] if "longName" in layer else layer["name"]))
            logger.debug(u"  datasource: {0}".format(layer.dataSource))

        return False

    return True


def _attr_shallow_eq(a, b, attr_key):
    return b[attr_key] == a[attr_key] if attr_key in a and attr_key in b else False


def _attr_deep_eq(a, b, attr_key):
    return _recursive_sort(a[attr_key]) == _recursive_sort(b[attr_key]) if attr_key in a and attr_key in b else False


def _match_layers(was_layers, now_layers):
    """Attempts to match layers from one set of layer descriptions to another.
    
    To correlate a layer in map a and map b, we run a series of specificity tests. Tests are ordered from most 
    specific, to least specific. These tests apply a process of elimination methodology to correlate layers between 
    the two maps
    """

    added = []
    matched = []
    removed = []
    resolved_was = {}
    resolved_now = {}
    is_resolved_was = lambda x: x['index'] in resolved_was
    is_resolved_now = lambda x: x['index'] in resolved_now
    same_id = lambda a, b: _attr_shallow_eq(a, b, 'serviceId')
    same_name = lambda a, b: _attr_shallow_eq(a, b, 'name')
    same_datasource = lambda a, b: dictionaries_eq_ignore_case(get_datasource_info(a), get_datasource_info(b))

    tests = [
        {
            # same id/name and datasource. Unchanged
            'fn': lambda a, b: b if same_id(a, b) and same_name(a, b) and same_datasource(a, b) else None,
            'ignore': True
        },
        {
            # same name and id, datasource changed
            'fn':
            lambda a, b: b
            if same_id(a, b) and same_name(a, b) and not is_resolved_was(a) and not is_resolved_now(b) else None
        },
        {
            # same id and datasource, name changed
            'fn':
            lambda a, b: b
            if same_id(a, b) and same_datasource(a, b) and not is_resolved_was(a) and not is_resolved_now(b) else None
        },
        {
            # same id. Assumed valid if fixed data sources enabled
            # TODO this should be skipped if we can verify that fixed layer IDs are not used
            'fn': lambda a, b: b if same_id(a, b) and not is_resolved_was(a) and not is_resolved_now(b) else None
        },
        {
            # same name and datasource, id changed
            'fn':
            lambda a, b: b
            if same_name(a, b) and same_datasource(a, b) and not is_resolved_was(a) and not is_resolved_now(b) else None
        },
        {
            # same name, id/datasource changed
            'fn': lambda a, b: b if same_name(a, b) and not is_resolved_was(a) and not is_resolved_now(b) else None
        }
    ]

    def test_if_matching_layer(was_layer, now_layer):
        for test in tests:
            matcher = test['fn']
            match = matcher(was_layer, now_layer)
            if match is not None:
                return True

        return False

    for now_layer in now_layers:
        found = False

        # Find A layer that correlates to B layer
        for was_layer in was_layers:
            found = test_if_matching_layer(was_layer, now_layer)
            if found:
                resolved_was[was_layer['index']] = now_layer
                resolved_now[now_layer['index']] = was_layer
                break

        # Added layers
        if found is False:
            resolved_now[now_layer['index']] = None
            added.append(now_layer)

    # Removed layers
    for was_layer in was_layers:
        if not is_resolved_was(was_layer):
            resolved_was[was_layer['index']] = None
            removed.append(was_layer)

    for was_layer in was_layers:
        resolved_layer = resolved_was[was_layer["index"]]
        if resolved_layer:
            matched.append((was_layer, resolved_layer))

    return (added, matched, removed)


def _compare_map_frames(was_map_desc, now_map_desc):
    """
    Compares two arcpy.mapping.DataFrame/arcpy.mp.Map objects for differences.

    Intended to be used to compare a historical version of a map with a new version, chiefly to look for changes that
    will impact the API of a map service built from the given map.
    """

    map_differences = {"map": [], "layers": {"added": [], "updated": [], "removed": []}, "tables": []}

    if was_map_desc is None:
        # new map introduced, ignore
        return map_differences

    map_doc_changes = MapChangeTypes.compare(was_map_desc, now_map_desc)
    map_differences["map"] = map_doc_changes

    (map_differences["layers"]["added"], matched,
     map_differences["layers"]["removed"]) = _match_layers(was_map_desc["layers"], now_map_desc["layers"])
    for (was_layer, now_layer) in matched:
        # make a shallow copy so we don't change the input description
        now_layer = now_layer.copy()
        now_layer["diff"] = LayerChangeTypes.compare(was_layer, now_layer)
        if len(now_layer["diff"]) > 0:
            map_differences["layers"]["updated"].append(now_layer)

    return map_differences


def _recursive_sort(obj):
    """
    Recursively sort lists/dictionaries for consistent comparison.
    """

    if isinstance(obj, dict):
        return sorted((k, _recursive_sort(v)) for k, v in obj.items())
    if isinstance(obj, list):
        return sorted(_recursive_sort(x) for x in obj)
    else:
        return obj
