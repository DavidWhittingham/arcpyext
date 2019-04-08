try:
    import arcpy.mapping
    from ._publishing import (convert_map_to_service_draft, convert_toolbox_to_service_draft,
                         convert_service_draft_to_staged_service, load_map_sddraft, load_image_sddraft,
                         load_geocode_sddraft, load_geodata_sddraft, load_gp_sddraft)
except:
    #TODO: import relevant things
    from ._publishing import convert_pro_project_to_service_draft as convert_map_to_service_draft
    from ._publishing import convert_service_draft_to_staged_service, load_image_sddraft, load_geocode_sddraft
