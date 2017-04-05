========
arcpyext
========

arcpyext provides a collection of helper functions that make common tasks performed with the Esri ArcPy site-package
easier to accomplish.  It was chiefly developed to service a command-line tool set (agstools) for managing ArcGIS
environments, but can readily be used within other scripts.

Features
===============

Currently, arcpyext has functionality for changing data sources for map document layers, preparing map documents for
publishing, and performing CRUD operations within an edit session on a geo-database.

arcpyext.data
-------------

The *data* module wraps the basic create, update and delete operations in an edit session, automatically starting/
stoping/aborting an edit operation as appropriate. The functions simply wrap the appropriate *arcpy.da* cursors, so
functionally they work identically. Also provided is a handy function for reading rows into a list.

Example:

.. code-block:: python

    import arcpy
    import arcpyext.data

    #WORKSPACE = "path/to/sde_database.sde"
    WORKSPACE = "path/to/geodatabase.gdb"
    TABLE = "Countries"

    edit_session = arcpy.da.Editor(WORKSPACE)
    edit_session.startEditing()

    try:
        arcpyext.data.delete_rows(edit_session, TABLE, "Name LIKE 'A%'", ('Name'))
    except RuntimeError, re:
        edit_session.stopEditing(False)

    edit_session.stopEditing(True)
    del edit_session

See the associated tests for more code examples.

arcpyext.mapping
----------------

The *mapping* module provides features for changing the data sources of a layer (or layers) in a map document.  Data
source changes can be templated (with simple match criteria) and then applied across an entire map document.

See the associated tests for code examples.

arcpyext.publishing
-------------------
The *publishing* modules provides features for publishing map, image and geo-processing services.  This currently
includes functionality for creating and/or editing Service Definition Drafts for each service type.
The following classes are provided in order to edit most of the common Service Definition Draft settings:
 - arcpyext.publishing.MapSDDraft
 - arcpyext.publishing.ImageSDDraft
 - arcpyext.publishing.GPSDDraft

See the associated test for code examples.
