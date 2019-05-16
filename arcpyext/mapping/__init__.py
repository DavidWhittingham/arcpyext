# import arcpy version-specific mapping modules
try:
    # py2 arcpy desktop
    import arcpy.mapping
    from ._mapping2 import (change_data_sources, create_replacement_data_sources_list, get_version,
                            list_document_data_sources, validate_map, compare, open_document)

except (AttributeError, ImportError):
    # py3 arcpy pro
    from ._mapping3 import (list_document_data_sources, change_data_sources, compare, validate_pro_project,
                            validate_map, create_replacement_data_sources_list, open_document)
