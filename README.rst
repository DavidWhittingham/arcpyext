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

arcpyext.conversion
-------------------

The *conversion* module features simple functions for converting workspaces (file geodatabase, enterprise geodatabase),
and the items in them, into other formats.

Supported formats are:

 - Shapefile
 - MapInfo TAB (requires the ArcGIS Data Interoperability extension)
 - GeoPackage
 - Office Open XML Workbook (Excel .xlsx file)
 - Comma-Separated Values text file

Example A - Convert File Geodatabase to a GeoPackage
....................................................

.. code-block:: python

    import arcpyext.conversion

    INPUT_WORKSPACE = "path/to/input_geodatbase.gdb"
    OUTPUT_GEOPACKAGE = "path/to/output/geopackage.gpkg"

    arcpyext.conversion.to_geopackage.workspace(INPUT_WORKSPACE, OUTPUT_GEOPACKAGE)

Example B - Convert File Geodatabase to an Office Open XML Spreadsheet (Excel spreadsheet)
..........................................................................................

.. code-block:: python

    import arcpyext.conversion

    INPUT_WORKSPACE = "path/to/input_geodatbase.gdb"
    OUTPUT_WORKBOOK = "path/to/output/workbook.xlsx"

    arcpyext.conversion.to_ooxml_workbook.workspace(INPUT_WORKSPACE, OUTPUT_WORKBOOK)

arcpyext.data
-------------

The *data* module wraps the basic create, update and delete operations in an edit session, automatically starting/
stoping/aborting an edit operation as appropriate. The functions simply wrap the appropriate *arcpy.da* cursors, so
functionally they work identically. Also provided is a handy function for reading rows into a list.

Example
.......

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

The *mapping* module provides features for:

 - describing a map document/project
 - changing the data sources of a layer (or layers) in an ArcGIS Map Document or ArcGIS Project,
 - easily checking if a map document/project is in a valid state
 - comparing different versions of a map document/project

Describing a Map Document/ArcGIS Project
........................................

Describing a map document/project productions a dictionary detailing many of the details about a map document. Map
documents/projects can be described as follows:

.. code-block:: python

    import arcpyext

    path_to_mxd_or_project = "path/to/arcgis/map_doc.mxd" # or *.aprx file on ArcGIS Pro

    description = arcpyext.mapping.describe(path_to_mxd_or_project)

The ouput description will have the following structure:

.. code-block:: python

    {
        "filePath": "C:\\projects\\public\\arcpyext\\tests\\samples\\test_mapping_complex.mxd",

        # an ordered list of maps contained in the map document/project
        "maps": [
            {
                "name": "Layers",
                "spatialReference": "GEOGCS['GCS_GDA_1994',DATUM['D_GDA_1994',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]];-400 -400 1000000000;-100000 10000;-100000 10000;8.98315284119521E-09;0.001;0.001;IsHighPrecision",
                
                # an ordered list of layers contained in the map
                "layers": [
                    {
                        "dataSource": "C:\\projects\\public\\arcpyext\\tests\\samples\\statesp020_clip1",
                        "database": "C:\\projects\\public\\arcpyext\\tests\\samples",
                        "datasetName": "statesp020_clip1",
                        "datasetType": "Shapefile Feature Class",
                        "definitionQuery": "FID <1",
                        "fields": [
                            {
                                "alias": "FID",
                                "index": 0,
                                "name": "FID",
                                "type": "OID",
                                "visible": true
                            },
                            {
                                "alias": "SHAPE",
                                "index": 1,
                                "name": "Shape",
                                "type": "Geometry",
                                "visible": true
                            },
                            {
                                "alias": "AREA",
                                "index": 2,
                                "name": "AREA",
                                "type": "Double",
                                "visible": true
                            },
                            {
                                "alias": "PERIMETER",
                                "index": 3,
                                "name": "PERIMETER",
                                "type": "Double",
                                "visible": true
                            },
                            {
                                "alias": "STATE",
                                "index": 5,
                                "name": "STATE",
                                "type": "String",
                                "visible": true
                            }
                        ],
                        "index": 0,
                        "isBroken": false,
                        "isFeatureLayer": true,
                        "isGroupLayer": false,
                        "isNetworkAnalystLayer": false,
                        "isRasterLayer": false,
                        "isRasterizingLayer": null,
                        "isServiceLayer": null,
                        "longName": "Layer 1",
                        "name": "Layer 1",
                        "server": null,
                        "service": null,
                        "serviceId": 1,
                        "userName": null,
                        "visible": true
                    }
                ],

                # an ordered list of the tables contained in the map
                "tables": [
                    {
                        "dataSource": "C:\\projects\\public\\arcpyext\\tests\\samples\\statesp020.txt",
                        "database": "C:\\projects\\public\\arcpyext\\tests\\samples",
                        "datasetName": "statesp020.txt",
                        "datasetType": "Text File",
                        "definitionQuery": "",
                        "fields": [
                            {
                                "alias": "Identification_Information:",
                                "index": 0,
                                "name": "Identification_Information:",
                                "type": "String",
                                "visible": true
                            }
                        ],
                        "index": 0,
                        "isBroken": false,
                        "name": "statesp020.txt",
                        "server": null,
                        "service": null,
                        "serviceId": 7,
                        "userName": null
                    }
                ]
            }
        ]
    }
 
Changing Data Sources
.....................

Changing data sources across both map documents and projects is made easy by creating templates with match criteria,
and then evaluating those templates against a map document or project to generate a list of replacement data sources
for layers that match.

Templates have slightly different structures depending on whether you are editing an ArcGIS Map Document or an ArcGIS Project.

ArcGIS Map Document:

.. code-block:: python

    "dataSource": {
        # The *dataSource* property points to the replacement data source
        # The contents of the property depends on whether your changing data sources on a map document or a project

        "workspacePath": "path/to/workspace/if/changed",
        "datasetName": "nameOfTheNewDatasetIfChanged",
        "wokspaceType": "workspaceTypeIfChanged",
        "schema": "databaseSchemaNameIfChanged"
    },
    "matchCriteria": {
        # properties that match against properties discovered when describing a layer
        # strings are compared ingoring case
        # an empty dictionary is also valid, which will match all layers

        # Changing user is a common use case for updating data sources
        "userName": "ExistingUserName"
    }

ArcGIS Project:

.. code-block:: python

    "dataSource": {
        # Any properties decribed at the following address under the *Using the connectionProperties dictionary*
        # section header are valid: https://pro.arcgis.com/en/pro-app/arcpy/mapping/updatingandfixingdatasources.htm
        
        # Example
        "connection_info": {
            "database": "path/to/database"
        },
        "dataset": "NewDataset"
    },
    "matchCriteria": {
        # properties that match against properties discovered when describing a layer
        # strings are compared ingoring case
        # an empty dictionary is also valid, which will match all layers

        # Changing user is a common use case for updating data sources
        "userName": "ExistingUserName"
    }

A list of templates can be used to create a replacement list of data sources for a map document or project.

.. code-block:: python

    import arcpyext

    path_to_mxd_or_project = "path/to/arcgis/map_doc.mxd" # or *.aprx file on ArcGIS Pro
    data_source_templates = [
        # one or more templates goes hear
        "dataSource": {
            "workspacePath": "./newDatabaseConnection.sde"
        },
        "matchCriteria": {
            # match everything
        }
    ]

    replacement_data_source_list = arcpyext.mapping.create_replacement_data_sources_list(
                                    path_to_mxd_or_project,
                                    data_source_templates)

The generated replacement data source list can then be fed back into *arcpyext* to update all of the matched layers
and tables:

.. code-block:: python

    arcpyext.mapping.change_data_sources(path_to_mxd_or_project, replacement_data_source_list)

Check a Map Is Valid
....................

A conveniance method exists to quickly test whether a map document/project is in a valid state or not (i.e. has broken
layers/tables or not).  This can be called as follows:

.. code-block:: python

    import arcpyext

    path_to_mxd_or_project = "path/to/arcgis/map_doc.mxd" # or *.aprx file on ArcGIS Pro

    arcpyext.mapping.is_valid(path_to_mxd_or_project)


arcpyext.publishing
-------------------
The *publishing* modules provides conveniant functions for creating service definition or drafts from the first map
in an ArcGIS Map Document or ArcGIS Project.

Create a Service Definition Draft from a Map Document
.....................................................

This function checks that the map does not have any broken data sources before crafting a service definition draft.

.. code-block:: python

    import arcpyext

    path_to_mxd_or_project = "path/to/arcgis/map_doc.mxd" # or *.aprx file on ArcGIS Pro
    output_path = "path/to/sddraft/output.sddraft"
    service_name = "ExampleMapService"
    
    arcpyext.publishing.convert_map_to_service_draft(path_to_mxd_or_project, output_path, service_name)
