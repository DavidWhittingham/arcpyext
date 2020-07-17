# coding=utf-8

import arcpy


def enrich_conn_props(conn_props, cim_part):
    """Adds featureDataset to the connection properties, accounting for recursive joins."""

    skip_this_level = False

    if "source" in conn_props:
        # table has joins, dive deeper
        enrich_conn_props(conn_props["source"], cim_part.sourceTable)

    if "destination" in conn_props:
        # table has joins, dive deeper
        enrich_conn_props(conn_props["destination"], cim_part.destinationTable)

    if not skip_this_level:
        # this level has the data
        if not "featureDataset" in conn_props:
            conn_props["featureDataset"] = cim_part.featureDataset if hasattr(cim_part, "featureDataset") else None


def is_query_layer(layer_cim):

    # get the table part of the CIM, unless the layer is a table already
    table_cim = layer_cim.featureTable if hasattr(layer_cim, "featureTable") else layer_cim

    if hasattr(table_cim, "dataConnection"):
        return isinstance(table_cim.dataConnection, arcpy.cim.CIMSqlQueryDataConnection) or isinstance(
            table_cim.dataConnection, arcpy.cim.CIMRelQueryTableDataConnection)

    return False


def recursive_process_connection_info(conn_props, current, new, cim_part):
    """Recursively processes the tables' connection properties, the provided connection infos, and the CIM to
    set featureDataset."""

    if "source" in current and "source" in new:
        # need to process next level
        recursive_process_connection_info(conn_props["source"], current["source"], new["source"], cim_part.sourceTable)

    if "destination" in current and "destination" in new:
        # need to process next level
        recursive_process_connection_info(conn_props["destination"], current["destination"], new["destination"],
                                          cim_part.destinationTable)

    if "featureDataset" in current and "featureDataset" in new:
        # need to process this level
        if conn_props["featureDataset"] == current["featureDataset"]:
            # need to replace feature dataset
            cim_part.featureDataset = new["featureDataset"]
            del current["featureDataset"]
            del new["featureDataset"]