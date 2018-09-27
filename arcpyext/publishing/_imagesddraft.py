from __future__ import (absolute_import, division, print_function, unicode_literals)
from builtins import (bytes, dict, int, list, object, range, str, ascii, chr, hex, input, next, oct, open, pow, round,
                      super, filter, map, zip)

from enum import Enum

from ._jpip_server_extension import JpipServerExtension
from ._sddraft_base import SDDraftBase
from ._sddraft_cacheable import SDDraftCacheable
from ._sddraft_image_dimensions import SDDraftImageDimensions
from ._sddraft_max_record_count import SDDraftMaxRecordCountMixin
from ._sddraft_output_dir import SDDraftOutputDirMixin
from ._wcs_server_extension import WcsServerExtension
from ._wms_server_extension import WmsServerExtension

class ImageSDDraft(SDDraftMaxRecordCountMixin, SDDraftOutputDirMixin, SDDraftCacheable, SDDraftImageDimensions, SDDraftBase):
    """Class for editing a Service Definition Draft for an Image Service.

    Must be instantiated from an existing on-disk Image SDDraft file."""

    class Capability(Enum):
        catalog = "Catalog"
        edit = "Edit"
        mensuration = "Mensuration"
        pixels = "Pixels"
        download = "Download"
        image = "Image"
        metadata = "Metadata"

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

    def __init__(self, editor):
        super(ImageSDDraft, self).__init__(editor)
        self._jpip_server_extension = JpipServerExtension(editor)
        self._wcs_server_extension = WcsServerExtension(editor)
        self._wms_server_extension = WmsServerExtension(editor)

    #####################
    # PUBLIC PROPERTIES #
    #####################

    @property
    def allowed_compressions(self):
        """Gets a list of the image compression methods (by type name) that are currently enabled for the service."""
        return [self.CompressionMethod(item) for item in
            self._editor.get_element_value(self._allowed_compressions_element).split(",")]

    @allowed_compressions.setter
    def allowed_compressions(self, values):
        """Sets the image compression methods (by an iterable of type names) that are enabled for the service.

        Valid values are contained in the 'arcpyext.mapping.ImageSDDraft.CompressionMethod' enumerated type.
        """
        self._editor.set_element_value(
            self._allowed_compressions_element,
            self._editor.enum_list_to_str(values, self.CompressionMethod, "Compression method specified is of an unknown type."))

    @property
    def allowed_fields(self):
        values = self._editor.get_element_value(self._allowed_fields_element)
        return values.split(",")

    @allowed_fields.setter
    def allowed_fields(self, values):
        self._editor.set_element_value(self._allowed_fields_element, ",".join(values))

    @property
    def allowed_mosaic_methods(self):
        return [self.MosaicMethod(item) for item in
            self._editor.get_element_value(self._allowed_mosaic_methods_element).split(",")]

    @allowed_mosaic_methods.setter
    def allowed_mosaic_methods(self, values):
        self._editor.set_element_value(
            self._allowed_mosaic_methods_element,
            self._editor.enum_list_to_str(values, self.MosaicMethod, "Mosaic method specified is of an unknown type."))

    @property
    def available_fields(self):
        values = self._editor.get_element_value(self._available_fields_element)
        return values.split(",")

    @available_fields.setter
    def available_fields(self, values):
        self._editor.set_element_value(self._available_fields_element, ",".join(values))

    @property
    def copyright(self):
        self._editor.get_element_value(self._copyright_elements[0])

    @copyright.setter
    def copyright(self, value):
        for elem in self._copyright_elements:
            self._editor.set_element_value(elem, value)

    @property
    def default_jpeg_compression_quality(self):
        return self._editor.get_element_value(self._default_jpeg_compression_quality_element)

    @default_jpeg_compression_quality.setter
    def default_jpeg_compression_quality(self, value):
        self._editor.set_element_value(
            self._default_jpeg_compression_quality_element,
            self._editor.verify_int(value, "Default JPEG Compression Quality", allow_none = False))

    @property
    def default_resampling_method(self):
        value = self._editor.get_element_value(self._default_resampling_method_element)
        return self.ResamplingMethod(int(value))

    @default_resampling_method.setter
    def default_resampling_method(self, value):
        if not isinstance(value, self.ResamplingMethod):
            value = self.ResamplingMethod(value)
        self._editor.set_element_value(self._default_resampling_method_element, value.value)

    @property
    def jpip_server(self):
        return self._jpip_server_extension

    @property
    def max_download_image_count(self):
        return self._editor.get_element_value(self._max_download_image_count_element)

    @max_download_image_count.setter
    def max_download_image_count(self, value):
        self._editor.set_element_value(
            self._max_download_image_count_element,
            self._editor.verify_int(value, "Maximum Download Image Count", allow_none = True))

    @property
    def max_download_size_limit(self):
        return self._editor.get_element_value(self._max_download_size_limit_element)

    @max_download_size_limit.setter
    def max_download_size_limit(self, value):
        self._editor.set_element_value(
            self._max_download_size_limit_element,
            self._editor.verify_int(value, "Maximum Download Size Limit", allow_none = True))

    @property
    def max_mosaic_image_count(self):
        return self._editor.get_element_value(self._max_mosaic_image_count_element)

    @max_mosaic_image_count.setter
    def max_mosaic_image_count(self, value):
        self._editor.set_element_value(
            self._max_mosaic_image_count_element,
            self._editor.verify_int(value, "Maximum Mosaic Count", allow_none = True))

    @property
    def return_jpgpng_as_jpg(self):
        return self._editor.value_to_boolean(self._editor.get_element_value(self._return_jpgpng_as_jpg_element))

    @return_jpgpng_as_jpg.setter
    def return_jpgpng_as_jpg(self, value):
        value = self._editor.value_to_boolean(value)
        self._editor.set_element_value(self._return_jpgpng_as_jpg_element, value)

    @property
    def wcs_server(self):
        """Gets the properties for the WCS Server extension."""
        return self._wcs_server_extension

    @property
    def wms_server(self):
        """Gets the properties for the WMS Server extension."""
        return self._wms_server_extension

    ######################
    # PRIVATE PROPERTIES #
    ######################

    @property
    def _allowed_compressions_element(self):
        return self._editor.get_value_element_by_key(self._config_props, "AllowedCompressions")

    @property
    def _allowed_fields_element(self):
        return self._editor.get_value_element_by_key(self._config_props, "AllowedFields")

    @property
    def _allowed_mosaic_methods_element(self):
        return self._editor.get_value_element_by_key(self._config_props, "AllowedMosaicMethods")

    @property
    def _available_fields_element(self):
        return self._editor.get_value_element_by_key(self._config_props, "AvailableFields")

    @property
    def _copyright_elements(self):
        return [
            self._editor.get_value_element_by_key(self._config_props, "copyright"),
            self._editor.get_first_element_by_tag("Credits", self._item_info_element)
        ]

    @property
    def _default_jpeg_compression_quality_element(self):
        return self._editor.get_value_element_by_key(self._config_props, "DefaultCompressionQuality")

    @property
    def _default_resampling_method_element(self):
        return self._editor.get_value_element_by_key(self._config_props, "DefaultResamplingMethod")

    @property
    def _description_elements(self):
        elem = super(ImageSDDraft, self)._description_elements

        elem.append(
            self._editor.get_value_element_by_key(self._config_props, "description")
        )

        return elem

    @property
    def _max_download_image_count_element(self):
        return self._editor.get_value_element_by_key(self._config_props, "MaxDownloadImageCount")

    @property
    def _max_download_size_limit_element(self):
        return self._editor.get_value_element_by_key(self._config_props, "MaxDownloadSizeLimit")

    @property
    def _max_mosaic_image_count_element(self):
        return self._editor.get_value_element_by_key(self._config_props, "MaxMosaicImageCount")

    @property
    def _return_jpgpng_as_jpg_element(self):
        return self._editor.get_value_element_by_key(self._config_props, "ReturnJPGPNGAsJPG")