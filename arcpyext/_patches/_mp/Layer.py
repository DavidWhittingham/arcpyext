# coding=utf-8
"""
This module contains patches to Esri's *arcpy._mp.Layer* class.  These patches may insert functionality or fix issues
directly in the *arcpy._mp.Layer* class.
"""

import arcpy

from .Field import Field
from .CimEditor import CimEditor


def add_fields():
    def fields_getter(self):
        layer_cim = self.getDefinition("V2")
        if hasattr(layer_cim, "featureTable"):
            return [Field(fd.fieldName, fd.alias, fd.visible) for fd in layer_cim.featureTable.fieldDescriptions]

        return None

    fields_prop = property(fields_getter)
    arcpy._mp.Layer.fields = fields_prop


def add_getManagedDefinition():
    def get_managed_definition(self, cim_version):
        return CimEditor(self, cim_version)

    arcpy._mp.Layer.getManagedDefinition = get_managed_definition


def enrich_connectionProperties():
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


def enrich_updateConnectionProperties():
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


add_fields()
add_getManagedDefinition()
enrich_connectionProperties()
enrich_updateConnectionProperties()