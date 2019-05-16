try:
    import arcpy.mapping
    from ._publishing import (convert_desktop_map_to_service_draft as convert_map_to_service_draft,
                              convert_toolbox_to_service_draft, convert_service_draft_to_staged_service)
except:
    from ._publishing import (convert_pro_map_to_service_draft as convert_map_to_service_draft,
                              convert_service_draft_to_staged_service)
