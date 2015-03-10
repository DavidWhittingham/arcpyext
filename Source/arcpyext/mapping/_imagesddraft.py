import codecs
import datetime
import re
import xml.etree.ElementTree as ET
import xml.dom.minidom as DOM

from enum import Enum

from _sddraftbase import SDDraftBase
from _sddraft_cacheable import SDDraftCacheable

class ImageSDDraft(SDDraftCacheable, SDDraftBase):
    """Class for editing a Service Definition Draft for an Image Service.

    Must be instantiated from an existing on-disk Image SDDraft file."""
    
    class CompressionMethod(Enum):
        none = "None"
        jpeg = "JPEG"
        lz77 = "LZ77"
        lerc = "LERC"
        
    class MosaicMethod(Enum):
        north_west = "NorthWest"
        center = "Center"
        lock_raster = "LockRaster"
        by_attribute = "ByAttribute"
        nadir = "Nadir"
        viewpoint = "Viewpoint"
        seamline = "Seamline"
        none = "None"
        
    class ResamplingMethod(Enum):
        nearest_neighbor = 0
        bilinear = 1
        cubic = 2
        majority = 3
    
    #Override.  MaxRecordCount key uses a capital "M" in an Image Service SDDraft. Why Esri, Why????
    _MAX_RECORD_COUNT_KEY = "MaxRecordCount"

    def __init__(self, path):
        super(ImageSDDraft, self).__init__(path)

    #####################
    # PUBLIC PROPERTIES #
    #####################

    @property
    def allowed_compressions(self):
        """Gets a list of the image compression methods (by type name) that are currently enabled for the service."""
        values = self._get_element_value(self._get_allowed_compressions_element())
        return [self.CompressionMethod(val) for val in values.split(",")]

    @allowed_compressions.setter
    def allowed_compressions(self, values):
        """Sets the image compression methods (by an iterable of type names) that are enabled for the service.

        Valid values are contained in the 'arcpyext.mapping.ImageSDDraft.CompressionMethod' enumerated type.
        """
        self._set_enum_val_list_to_element(
            values, 
            self.CompressionMethod, 
            self._get_allowed_compressions_element(), 
            "Compression method specified is of an unknown type.")

    @property
    def allowed_mosaic_methods(self):
        values = self._get_element_value(self._get_allowed_mosaic_methods_element())
        return [self.MosaicMethod(val) for val in values.split(",")]
    
    @allowed_mosaic_methods.setter
    def allowed_mosaic_methods(self, values):
        self._set_enum_val_list_to_element(
            values, 
            self.MosaicMethod, 
            self._get_allowed_mosaic_methods_element(), 
            "Mosaic method specified is of an unknown type.")
    
    @property
    def available_fields(self):
        values = self._get_element_value(self._get_available_fields_element())
        return values.split(",")

    @available_fields.setter
    def available_fields(self, values):
        self._set_element_value(self._get_available_fields_element(), ",".join(values))

    @property
    def default_resampling_method(self):
        value = self._get_element_value(self._get_default_resampling_method_element())
        return self.ResamplingMethod(int(value))

    @default_resampling_method.setter
    def default_resampling_method(self, value):
        if not isinstance(value, self.ResamplingMethod):
            value = self.ResamplingMethod(value)
        self._set_element_value(self._get_default_resampling_method_element(), value.value)

    @property
    def max_image_height(self):
        value = self._get_element_value(self._get_max_image_height_element())
        return int(value) if value else None

    @max_image_height.setter
    def max_image_height(self, value):
        if value != None and value < 0:
            raise ValueError("Image height cannot be less than zero.")
        self._set_element_value(self._get_max_image_height_element(), value)

    @property
    def max_image_width(self):
        value = self._get_element_value(self._get_max_image_width_element())
        return int(value) if value else None

    @max_image_width.setter
    def max_image_width(self, value):
        if value != None and value < 0:
            raise ValueError("Image width cannot be less than zero.")
        self._set_element_value(self._get_max_image_width_element(), value)

    @property
    def max_mosaic_image_count(self):
        value = self._get_element_value(self._get_max_mosaic_image_count_element())
        return int(value) if value else None

    @max_mosaic_image_count.setter
    def max_mosaic_image_count(self, value):
        if value != None and value < 0:
            raise ValueError("Maximum mosaic count cannot be less than zero.")
        self._set_element_value(self._get_max_mosaic_image_count_element(), value)

    ######################
    # PRIVATE PROPERTIES #
    ######################

    def _get_allowed_compressions_element(self):
        return self._get_value_element_by_key(self._get_service_config_props(), "AllowedCompressions")
        
    def _get_allowed_mosaic_methods_element(self):
        return self._get_value_element_by_key(self._get_service_config_props(), "AllowedMosaicMethods")
    
    def _get_available_fields_element(self):
        return self._get_value_element_by_key(self._get_service_config_props(), "AvailableFields")

    def _get_default_resampling_method_element(self):
        return self._get_value_element_by_key(self._get_service_config_props(), "DefaultResamplingMethod")

    def _get_max_image_height_element(self):
        return self._get_value_element_by_key(self._get_service_config_props(), "MaxImageHeight")

    def _get_max_image_width_element(self):
        return self._get_value_element_by_key(self._get_service_config_props(), "MaxImageWidth")

    def _get_max_mosaic_image_count_element(self):
        return self._get_value_element_by_key(self._get_service_config_props(), "MaxMosaicImageCount")
        
    def _set_enum_val_list_to_element(self, values, enum, element, exception_message):
        string_values = []
        for val in values:
            if isinstance(val, basestring):
                val = enum(val)
            elif not isinstance(val, enum):
                raise TypeError(exception_message)
            string_values.append(val.value)
                
        self._set_element_value(element, ",".join(string_values))