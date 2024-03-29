# coding=utf-8
"""
This module contains patches to Esri's *arcpy._mp.Table* class.  These patches may insert functionality or fix issues
directly in the *arcpy._mp.Table* class.
"""

import arcpy

from .Field import Field
from .CimEditor import CimEditor
from ._cim_helpers import enrich_conn_props, recursive_process_connection_info, is_query_layer


def add_fields():
    def fields_getter(self):
        table_cim = self.getDefinition("V2")
        return [Field(fd.fieldName, fd.alias, fd.visible) for fd in table_cim.fieldDescriptions]

    fields_prop = property(fields_getter)
    arcpy._mp.Table.fields = fields_prop


def add_getManagedDefinition():
    def get_managed_definition(self, cim_version):
        return CimEditor(self, cim_version)

    arcpy._mp.Table.getManagedDefinition = get_managed_definition


def enrich_connectionProperties():
    """On ArcGIS Pro, add support for feature dataset to the connectionProperties of the Table class, via the CIM."""

    # save the original connectionProperties property so we can call it later
    orig_table_connection_properties = arcpy._mp.Table.connectionProperties

    def connection_properties_getter(self):
        """New getter for getting connection properties and including 'featureDataset'."""

        conn_props = orig_table_connection_properties.__get__(self)
        table_cim = self.getDefinition("V2")

        enrich_conn_props(conn_props, table_cim.dataConnection)

        return conn_props

    connection_properties_prop = property(connection_properties_getter)
    arcpy._mp.Table.connectionProperties = connection_properties_prop


def enrich_updateConnectionProperties():
    """On ArcGIS Pro, add support for feature dataset to the updateConnectionProperties of the Table class, via the CIM."""

    # save the original updateConnectionProperties function so we can call it later
    orig_table_updateConnectionProperties = arcpy._mp.Table.updateConnectionProperties

    def extended_update_connection_properties(self, current_connection_info, new_connection_info, *args, **kwargs):
        """Extends updateConnectionProperties with support for setting featureDataset via CIM."""

        if isinstance(current_connection_info, dict) and isinstance(new_connection_info, dict):
            # only process if connection infos are dictionaries
            table_conn_props = self.connectionProperties
            table_cim = self.getDefinition("V2")
            # query tables can't have their definition set, the layer ends up broken
            if not is_query_layer(table_cim):
                recursive_process_connection_info(
                    table_conn_props, current_connection_info, new_connection_info, table_cim.dataConnection
                )
                self.setDefinition(table_cim)

        return orig_table_updateConnectionProperties(
            self, current_connection_info, new_connection_info, *args, **kwargs
        )

    arcpy._mp.Table.updateConnectionProperties = extended_update_connection_properties


add_fields()
add_getManagedDefinition()
enrich_connectionProperties()
enrich_updateConnectionProperties()