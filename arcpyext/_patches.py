# coding=utf-8
"""
This module handles applying patches to Esri's *arcpy* module.  These patches may insert functionality or fix issues
directly in the *arcpy* module.
"""

# Python 2/3 compatibility
# pylint: disable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position
from __future__ import (absolute_import, division, print_function, unicode_literals)
from future.builtins.disabled import *
from future.builtins import *
from future.standard_library import install_aliases
install_aliases()
# pylint: enable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position

import arcpy
import re
import sys

from decimal import Decimal


def apply():
    """
    Applies all the patches contained is this module.
    """

    fix_mapping_versions()

    if sys.version_info[0] == 3:
        py3_enrich_connectionProperties()
        py3_enrich_updateConnectionProperties()


def fix_mapping_versions():
    """
    This function monkey patches the mapping version information in arcpy to support the currently installed version,
    along with past versions if they are not included (arcpy 10.5 does not have 10.4 supported version, but the
    support is there under the hood).
    """

    # get ArcGIS version as a number
    ags_version = Decimal(re.search(r"^(\d+\.\d+)", arcpy.GetInstallInfo()['Version'], re.IGNORECASE).group(1))

    # surrounded in try/pass to fail gracefully in case Esri change the design of this internal API
    try:
        versions = arcpy._mapping.constants.__args__["version"]

        if ags_version >= Decimal("10.4") and "10.4" not in versions:
            versions["10.4"] = 104

        if ags_version >= Decimal("10.5") and "10.5" not in versions:
            versions["10.5"] = 105

        if ags_version >= Decimal("10.6") and "10.6" not in versions:
            versions["10.6"] = 106
    except:
        pass


def py3_enrich_connectionProperties():
    """On ArcGIS Pro, add support for feature dataset to the connectionProperties of the Layer class, via the CIM."""

    # save the original connectionProperties property so we can call it later
    orig_layer_connection_properties = arcpy._mp.Layer.connectionProperties

    def connection_properties_getter(self):
        """New getter for getting connection properties and including 'featureDataset'."""
        def enrich_conn_props(conn_props, cim_part):
            """Adds featureDataset to the connection properties, accounting for recursive joins."""

            skip_this_level = False

            if "source" in conn_props:
                # layer has joins, dive deeper
                enrich_conn_props(conn_props["source"], cim_part.sourceTable)

            if "destination" in conn_props:
                # layer has joins, dive deeper
                enrich_conn_props(conn_props["destination"], cim_part.destinationTable)

            if not skip_this_level:
                # this level has the data
                if not "featureDataset" in conn_props:
                    conn_props["featureDataset"] = cim_part.featureDataset if hasattr(cim_part,
                                                                                      "featureDataset") else None

        conn_props = orig_layer_connection_properties.__get__(self)
        layer_cim = self.getDefinition("V2")

        if hasattr(layer_cim, "featureTable"):
            enrich_conn_props(conn_props, layer_cim.featureTable.dataConnection)

        return conn_props

    connection_properties_prop = property(connection_properties_getter)
    arcpy._mp.Layer.connectionProperties = connection_properties_prop


def py3_enrich_updateConnectionProperties():
    """On ArcGIS Pro, add support for feature dataset to the updateConnectionProperties of the Layer class, via the CIM."""

    # save the original updateConnectionProperties function so we can call it later
    orig_layer_updateConnectionProperties = arcpy._mp.Layer.updateConnectionProperties

    def extended_update_connection_properties(self, current_connection_info, new_connection_info, *args, **kwargs):
        """Extends updateConnectionProperties with support for setting featureDataset via CIM."""
        def recursive_process_connection_info(layer_conn_props, current, new, cim_part):
            """Recursively processes the layers connection properties, the provided connection infos, and the CIM to
            set featureDataset."""

            if "source" in current and "source" in new:
                # need to process next level
                recursive_process_connection_info(layer_conn_props["source"], current["source"], new["source"],
                                                  cim_part.sourceTable)

            if "destination" in current and "destination" in new:
                # need to process next level
                recursive_process_connection_info(layer_conn_props["destination"], current["destination"],
                                                  new["destination"], cim_part.destinationTable)

            if "featureDataset" in current and "featureDataset" in new:
                # need to process this level
                if layer_conn_props["featureDataset"] == current["featureDataset"]:
                    # need to replace feature dataset
                    cim_part.featureDataset = new["featureDataset"]

        if isinstance(current_connection_info, dict) and isinstance(new_connection_info, dict):
            # only process if connection infos are dictionaries
            layer_conn_props = self.connectionProperties
            layer_cim = self.getDefinition("V2")
            if hasattr(layer_cim, "featureTable"):
                recursive_process_connection_info(layer_conn_props, current_connection_info, new_connection_info,
                                                  layer_cim.featureTable.dataConnection)
                self.setDefinition(layer_cim)

        return orig_layer_updateConnectionProperties(self, current_connection_info, new_connection_info, *args,
                                                     **kwargs)

    arcpy._mp.Layer.updateConnectionProperties = extended_update_connection_properties
