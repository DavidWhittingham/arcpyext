# Python 2/3 compatibility
from __future__ import (absolute_import, division, print_function, unicode_literals)
from future.builtins import *
from future.builtins.disabled import *
from future.standard_library import install_aliases
install_aliases()

import arcpy

def create_rows(edit_session, in_table, rows, field_names = "*"):
    _create_rows(edit_session, in_table, rows, field_names)

def delete_rows(edit_session, in_table, where_clause = None, field_names = "*"):
    _delete_rows(edit_session, in_table, where_clause, field_names)

def read_rows(in_table, where_clause = None, field_names = "*"):
    with arcpy.da.SearchCursor(in_table, field_names, where_clause) as cursor:
        rows = [row for row in cursor]
    return rows

def update_rows_func(edit_session, in_table, update_func, where_clause = None, field_names = "*"):
    _update_rows_func(edit_session, in_table, update_func, where_clause, field_names)

###############################################################################
# PRIVATE FUNCTIONS
###############################################################################
def _edit_handler(func):
    def wrapper(*args):
        edit_session = args[0]

        edit_session.startOperation()

        try:
            func(*args)
        except Exception:
            edit_session.abortOperation()
            raise

        edit_session.stopOperation()

    return wrapper

@_edit_handler
def _create_rows(edit_session, in_table, rows, field_names):
    with arcpy.da.InsertCursor(in_table, field_names) as cursor:
        for row in rows:
            cursor.insertRow(row)

@_edit_handler
def _delete_rows(edit_session, in_table, where_clause, field_names):
    with arcpy.da.UpdateCursor(in_table, field_names, where_clause) as cursor:
        for row in cursor:
            cursor.deleteRow()

@_edit_handler
def _update_rows_func(edit_session, in_table, update_func, where_clause, field_names):
    with arcpy.da.UpdateCursor(in_table, field_names, where_clause) as cursor:
        for row in cursor:
            cursor.updateRow(update_func(row))
