# Determine the environment and get appropriate methods
try:
    import arcpy.mapping
    from ._arcobjects import init_arcobjects_context, destroy_arcobjects_context, list_layers, mxd_exists, open_mxd
except:
    from ._proobjects import init_arcobjects_context, destroy_arcobjects_context, list_layers, project_exists, open_project, create_project
