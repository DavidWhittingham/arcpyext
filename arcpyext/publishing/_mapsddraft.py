from enum import Enum

from ._feature_server_extension import FeatureServerExtension
from ._kml_server_extension import KmlServerExtension
from ._mobile_server_extension import MobileServerExtension
from ._na_server_extension import NaServerExtension
from ._schematics_server_extension import SchematicsServerExtension
from ._sddraft_base import SDDraftBase
from ._sddraft_cacheable import SDDraftCacheable
from ._sddraft_image_dimensions import SDDraftImageDimensions
from ._wcs_server_extension import WcsServerExtension
from ._wfs_server_extension import WfsServerExtension
from ._wms_server_extension import WmsServerExtension

class MapSDDraft(SDDraftCacheable, SDDraftImageDimensions, SDDraftBase):
    """Class for editing a Service Definition Draft.

    Must be instantiated from an on-disk SDDraft file generated."""

    class AntiAliasingMode(Enum):
        none = "None"
        fastest = "Fastest"
        fast = "Fast"
        normal = "Normal"
        best = "Best"

    class Capability(Enum):
        map = "Map"
        query = "Query"
        data = "Data"

    class TextAntiAliasingMode(Enum):
        none = "None"
        force = "Force"
        normal = "Normal"

    def __init__(self, editor):
        super(MapSDDraft, self).__init__(editor)
        self._feature_server_extension = FeatureServerExtension(editor)
        self._kml_server_extension = KmlServerExtension(editor)
        self._mobile_server_extension = MobileServerExtension(editor)
        self._na_server_extension = NaServerExtension(editor)
        self._schematics_server_extension = SchematicsServerExtension(editor)
        self._wcs_server_extension = WcsServerExtension(editor)
        self._wfs_server_extension = WfsServerExtension(editor)
        self._wms_server_extension = WmsServerExtension(editor)

    #region Properties

    @property
    def anti_aliasing_mode(self):
        """Gets the current anti-aliasing mode for map graphics."""
        return self.AntiAliasingMode(self._editor.get_element_value(self._anti_aliasing_element))

    @anti_aliasing_mode.setter
    def anti_aliasing_mode(self, value):
        """Sets the anti-aliasing mode for map graphics.

        Valid values are contained in the 'arcpyext.mapping.MapSDDraft.AntiAliasingMode' enumerated type.
        """
        if not isinstance(value, self.AntiAliasingMode):
            value = self.AntiAliasingMode(value)
        self._editor.set_element_value(self._anti_aliasing_element, value.value)

    @property
    def disable_identify_relates(self):
        """Gets a boolean indicating whether or not displaying related information in identify results is enabled."""
        return self._editor.value_to_boolean(
            self._editor.get_element_value(
                self._disable_identify_relates_element))

    @disable_identify_relates.setter
    def disable_identify_relates(self, value):
        value = self._editor.value_to_boolean(value)
        self._editor.set_element_value(
            self._disable_identify_relates_element,
            value)

    @property
    def enable_dynamic_layers(self):
        """Gets a boolean value indicating whether or not dynamic layer order and symbology are enabled."""
        return self._editor.value_to_boolean(
            self._editor.get_element_value(
                self._enable_dynamic_layers_element))

    @enable_dynamic_layers.setter
    def enable_dynamic_layers(self, value):
        """Gets a boolean value indicating whether or not dynamic layer order and symbology are enabled."""
        value = self._editor.value_to_boolean(value)
        self._editor.set_element_value(
            self._enable_dynamic_layers_element,
            value)

    @property
    def feature_server(self):
        """Gets the properties for the Feature Server (Feature Access in Web UI) extension."""
        return self._feature_server_extension

    @property
    def folder(self):
        """Gets the name of the folder that the service will reside in."""
        return super(MapSDDraft, self).folder

    @folder.setter
    def folder(self, value):
        """Sets the name of the folder that the service will reside in."""
        existing_full_path = self._get_full_path()
        SDDraftBase.folder.fset(self, value)
        self._set_full_path_properties(existing_full_path, self._get_full_path())

    @property
    def kml_server(self):
        """Gets the properties for the KML Server extension."""
        return self._kml_server_extension

    @property
    def mobile_server(self):
        """Gets the properties for the Mobile (Mobile Data Access in the UI) server extension."""
        return self._mobile_server_extension

    @property
    def na_server(self):
        """Gets the properties for the Network Analysis server extension"""
        return self._na_server_extension

    @property
    def name(self):
        """Gets the name of the service."""
        return super(MapSDDraft, self).name

    @name.setter
    def name(self, value):
        """Sets the name of the service (Cannot be an empty value)."""
        existing_full_path = self._get_full_path()

        # Change the name field on service extensions if they match the current name
        # If they don't match, assume they have been intentionally modified and leave them alone
        if self.wcs_server.name == self.name:
            self.wcs_server.name = value
        if self.wms_server.name == self.name:
            self.wms_server.name = value
        if self.wfs_server.name == self.name:
            self.wfs_server.name = value

        # Set the underlying value from base class and then update properties that are built from the full path
        SDDraftBase.name.fset(self, value)
        self._set_full_path_properties(existing_full_path, self._get_full_path())

    @property
    def schema_locking_enabled(self):
        """Gets a boolean indicating whether or not the server locks the database schema."""
        return self._editor.value_to_boolean(self._editor.get_element_value(self._schema_locking_enabled_element))

    @schema_locking_enabled.setter
    def schema_locking_enabled(self, value):
        """Sets a boolean indicating whether or not the server locks the database schema."""
        value = self._editor.value_to_boolean(value)
        self._editor.set_element_value(self._schema_locking_enabled_element, value)

    @property
    def schematics_server(self):
        """Gets the properties for the Schematics Server extension."""
        return self._schematics_server_extension

    @property
    def text_anti_aliasing_mode(self):
        """Gets the current anti-aliasing mode for map text."""
        return self.TextAntiAliasingMode(self._editor.get_element_value(self._text_anti_aliasing_element))

    @text_anti_aliasing_mode.setter
    def text_anti_aliasing_mode(self, value):
        """Sets the anti-aliasing mode for map graphics.

        Valid values are contained in the 'arcpyext.mapping.MapSDDraft.TextAntiAliasingMode' enumerated type.
        """
        if not isinstance(value, self.TextAntiAliasingMode):
            value = self.TextAntiAliasingMode(value)
        self._editor.set_element_value(self._text_anti_aliasing_element, value.value)

    @property
    def wcs_server(self):
        """Gets the properties for the WCS Server extension."""
        return self._wcs_server_extension

    @property
    def wfs_server(self):
        """Gets the properties for the WFS Server extension."""
        return self._wfs_server_extension

    @property
    def wms_server(self):
        """Gets the properties for the WMS Server extension."""
        return self._wms_server_extension

    @property
    def _anti_aliasing_element(self):
        return self._editor.get_value_element_by_key(self._config_props, "antialiasingMode")

    @property
    def _disable_identify_relates_element(self):
        return self._editor.get_value_element_by_key(
            self._config_props,
            "disableIdentifyRelates")

    @property
    def _enable_dynamic_layers_element(self):
        return self._editor.get_value_element_by_key(
            self._config_props,
            "enableDynamicLayers")

    @property
    def _schema_locking_enabled_element(self):
        return self._editor.get_value_element_by_key(self._config_props, "schemaLockingEnabled")

    @property
    def _text_anti_aliasing_element(self):
        return self._editor.get_value_element_by_key(self._config_props, "textAntialiasingMode")

    #endregion

    #region Methods

    def _set_full_path_properties(self, old_path, new_path):
        """Sets the value for properties that are dependent on both the folder name and the service name.

        Only sets the values if they haven't been changed from the default "folder_name" value.
        """
        if self.wfs_server.app_schema_prefix == old_path:
            self.wfs_server.app_schema_prefix = new_path

        if self.wcs_server.title == old_path:
            self.wcs_server.title = new_path

    def _get_full_path(self):
        return "{0}_{1}".format(self.folder, self.name) if self.folder != None else self.name

    #endregion