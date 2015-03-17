import codecs
import datetime
import re
import xml.etree.ElementTree as ET
import xml.dom.minidom as DOM

from enum import Enum

from ._sddraftbase import SDDraftBase
from ._sddraft_cacheable import SDDraftCacheable

class ImageSDDraft(SDDraftCacheable, SDDraftBase):
    """Class for editing a Service Definition Draft for an Image Service.

    Must be instantiated from an existing on-disk Image SDDraft file."""

    class CompressionMethod(Enum):
        none = "None"
        jpeg = "JPEG"
        lz77 = "LZ77"
        lerc = "LERC"

    class Extension(Enum):
        wmsserver = "WMSServer"
        wcsserver = "WCSServer"
        jpipserver = "JPIPServer"

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
    def max_download_image_count(self):
        return self._get_int_value_from_element(self._get_max_download_image_count_element())

    @max_download_image_count.setter
    def max_download_image_count(self, value):
        self._set_int_value_to_element(value, self._get_max_download_image_count_element(),
            "Maximum Download Image Count", allow_none = True)

    @property
    def max_download_size_limit(self):
        return self._get_int_value_from_element(self._get_max_download_size_limit_element())

    @max_download_size_limit.setter
    def max_download_size_limit(self, value):
        self._set_int_value_to_element(value, self._get_max_download_size_limit_element(),
            "Maximum Download Size Limit", allow_none = True)

    @property
    def max_image_height(self):
        return self._get_int_value_from_element(self._get_max_image_height_element())

    @max_image_height.setter
    def max_image_height(self, value):
        self._set_int_value_to_element(value, self._get_max_image_height_element(),
            "Maximum Image Height", allow_none = True)

    @property
    def max_image_width(self):
        return self._get_int_value_from_element(self._get_max_image_width_element())

    @max_image_width.setter
    def max_image_width(self, value):
        self._set_int_value_to_element(value, self._get_max_image_width_element(),
            "Maximum Image Width", allow_none = True)

    @property
    def max_mosaic_image_count(self):
        return self._get_int_value_from_element(self._get_max_mosaic_image_count_element())

    @max_mosaic_image_count.setter
    def max_mosaic_image_count(self, value):
        self._set_int_value_to_element(value, self._get_max_mosaic_image_count_element(),
            "Maximum Mosaic Count", allow_none = True)

    @property
    def return_jpgpng_as_jpg(self):
        return self._value_to_boolean(self._get_element_value(self._get_return_jpgpng_as_jpg_element()))

    @return_jpgpng_as_jpg.setter
    def return_jpgpng_as_jpg(self, value):
        value = self._value_to_boolean(value)
        self._set_element_value(self._get_return_jpgpng_as_jpg_element(), value)

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

    def _get_max_download_image_count_element(self):
        return self._get_value_element_by_key(self._get_service_config_props(), "MaxDownloadImageCount")

    def _get_max_download_size_limit_element(self):
        return self._get_value_element_by_key(self._get_service_config_props(), "MaxDownloadSizeLimit")

    def _get_max_image_height_element(self):
        return self._get_value_element_by_key(self._get_service_config_props(), "MaxImageHeight")

    def _get_max_image_width_element(self):
        return self._get_value_element_by_key(self._get_service_config_props(), "MaxImageWidth")

    def _get_max_mosaic_image_count_element(self):
        return self._get_value_element_by_key(self._get_service_config_props(), "MaxMosaicImageCount")

    def _get_return_jpgpng_as_jpg_element(self):
        return self._get_value_element_by_key(self._get_service_config_props(), "ReturnJPGPNGAsJPG")