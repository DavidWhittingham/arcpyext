from enum import Enum

from ._jpip_server_extension import JpipServerExtension
from ._sddraft_base import SDDraftBase
from ._sddraft_cacheable import SDDraftCacheable
from ._wcs_server_extension import WcsServerExtension
from ._wms_server_extension import WmsServerExtension

class ImageSDDraft(SDDraftCacheable, SDDraftBase):
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
            self._editor.get_element_value(self._get_allowed_compressions_element()).split(",")]

    @allowed_compressions.setter
    def allowed_compressions(self, values):
        """Sets the image compression methods (by an iterable of type names) that are enabled for the service.

        Valid values are contained in the 'arcpyext.mapping.ImageSDDraft.CompressionMethod' enumerated type.
        """
        self._editor.set_element_value(
            self._get_allowed_compressions_element(),
            self._editor.enum_list_to_str(values, self.CompressionMethod, "Compression method specified is of an unknown type."))

    @property
    def allowed_mosaic_methods(self):
        return [self.MosaicMethod(item) for item in
            self._editor.get_element_value(self._get_allowed_mosaic_methods_element()).split(",")]

    @allowed_mosaic_methods.setter
    def allowed_mosaic_methods(self, values):
        self._editor.set_element_value(
            self._get_allowed_mosaic_methods_element(),
            self._editor.enum_list_to_str(values, self.MosaicMethod, "Mosaic method specified is of an unknown type."))

    @property
    def available_fields(self):
        values = self._editor.get_element_value(self._get_available_fields_element())
        return values.split(",")

    @available_fields.setter
    def available_fields(self, values):
        self._editor.set_element_value(self._get_available_fields_element(), ",".join(values))

    @property
    def default_resampling_method(self):
        value = self._editor.get_element_value(self._get_default_resampling_method_element())
        return self.ResamplingMethod(int(value))

    @default_resampling_method.setter
    def default_resampling_method(self, value):
        if not isinstance(value, self.ResamplingMethod):
            value = self.ResamplingMethod(value)
        self._editor.set_element_value(self._get_default_resampling_method_element(), value.value)

    @property
    def jpip_server(self):
        return self._jpip_server_extension

    @property
    def max_download_image_count(self):
        return self._editor.get_element_value(self._get_max_download_image_count_element())

    @max_download_image_count.setter
    def max_download_image_count(self, value):
        self._editor.set_element_value(
            self._get_max_download_image_count_element(),
            self._editor.verify_int(value, "Maximum Download Image Count", allow_none = True))

    @property
    def max_download_size_limit(self):
        return self._editor.get_element_value(self._get_max_download_size_limit_element())

    @max_download_size_limit.setter
    def max_download_size_limit(self, value):
        self._editor.set_element_value(
            self._get_max_download_size_limit_element(),
            self._editor.verify_int(value, "Maximum Download Size Limit", allow_none = True))

    @property
    def max_image_height(self):
        return self._editor.get_element_value(self._get_max_image_height_element())

    @max_image_height.setter
    def max_image_height(self, value):
        self._editor.set_element_value(
            self._get_max_image_height_element(),
            self._editor.verify_int(value, "Maximum Download Height", allow_none = True))

    @property
    def max_image_width(self):
        return self._editor.get_element_value(self._get_max_image_width_element())

    @max_image_width.setter
    def max_image_width(self, value):
        self._editor.set_element_value(
            self._get_max_image_width_element(),
            self._editor.verify_int(value, "Maximum Download Width", allow_none = True))

    @property
    def max_mosaic_image_count(self):
        return self._editor.get_element_value(self._get_max_mosaic_image_count_element())

    @max_mosaic_image_count.setter
    def max_mosaic_image_count(self, value):
        self._editor.set_element_value(
            self._get_max_mosaic_image_count_element(),
            self._editor.verify_int(value, "Maximum Mosaic Count", allow_none = True))

    @property
    def return_jpgpng_as_jpg(self):
        return self._editor.value_to_boolean(self._editor.get_element_value(self._get_return_jpgpng_as_jpg_element()))

    @return_jpgpng_as_jpg.setter
    def return_jpgpng_as_jpg(self, value):
        value = self._editor.value_to_boolean(value)
        self._editor.set_element_value(self._get_return_jpgpng_as_jpg_element(), value)

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

    def _get_allowed_compressions_element(self):
        return self._editor.get_value_element_by_key(self._config_props, "AllowedCompressions")

    def _get_allowed_mosaic_methods_element(self):
        return self._editor.get_value_element_by_key(self._config_props, "AllowedMosaicMethods")

    def _get_available_fields_element(self):
        return self._editor.get_value_element_by_key(self._config_props, "AvailableFields")

    def _get_default_resampling_method_element(self):
        return self._editor.get_value_element_by_key(self._config_props, "DefaultResamplingMethod")

    def _get_max_download_image_count_element(self):
        return self._editor.get_value_element_by_key(self._config_props, "MaxDownloadImageCount")

    def _get_max_download_size_limit_element(self):
        return self._editor.get_value_element_by_key(self._config_props, "MaxDownloadSizeLimit")

    def _get_max_image_height_element(self):
        return self._editor.get_value_element_by_key(self._config_props, "MaxImageHeight")

    def _get_max_image_width_element(self):
        return self._editor.get_value_element_by_key(self._config_props, "MaxImageWidth")

    def _get_max_mosaic_image_count_element(self):
        return self._editor.get_value_element_by_key(self._config_props, "MaxMosaicImageCount")

    def _get_return_jpgpng_as_jpg_element(self):
        return self._editor.get_value_element_by_key(self._config_props, "ReturnJPGPNGAsJPG")