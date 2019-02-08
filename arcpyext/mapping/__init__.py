# explictly break if arcpy.mapping does not exist
try:
    import arcpy.mapping
except (AttributeError, ImportError):
    raise

from ._mapping import change_data_sources, create_replacement_data_sources_list, list_document_data_sources, validate_map, compare
