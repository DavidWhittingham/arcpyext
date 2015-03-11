from enum import Enum

from _sddraftbase import SDDraftBase
from _sddraft_cacheable import SDDraftCacheable

class SDDraft(SDDraftCacheable, SDDraftBase):
    """Class for editing a Service Definition Draft.

    Must be instantiated from an on-disk SDDraft file generated."""
    
    class AntiAliasingMode(Enum):
        none = "None"
        fastest = "Fastest"
        fast = "Fast"
        normal = "Normal"
        best = "Best"

    class Extension(Enum):
        featureserver = "FeatureServer"
        mobileserver = "MobileServer"
        wmsserver = "WMSServer"
        kmlserver = "KmlServer"
        naserver = "NAServer"
        wfsserver = "WFSServer"
        wcsserver = "WCSServer"
        schematicsserver = "SchematicsServer"
        
    class FeatureAccessOperation(Enum):
        create = "Create"
        query = "Query"
        update = "Update"
        delete = "Delete"
        sync = "Sync"

    class TextAntiAliasingMode(Enum):
        none = "None"
        force = "Force"
        normal = "Normal"

    _FEATURE_ACCESS_EDIT_OPERATIONS = ["Create", "Delete", "Update"]

    def __init__(self, path):
        super(SDDraft, self).__init__(path)

    #####################
    # PUBLIC PROPERTIES #
    #####################

    @property
    def anti_aliasing_mode(self):
        """Gets the current anti-aliasing mode for map graphics."""
        return self.AntiAliasingMode(self._get_element_value(self._get_anti_aliasing_element()))

    @anti_aliasing_mode.setter
    def anti_aliasing_mode(self, value):
        """Sets the anti-aliasing mode for map graphics.

        Valid values are contained in the 'arcpyext.mapping.SDDraft.AntiAliasingMode' enumerated type.
        """
        if not isinstance(value, self.AntiAliasingMode):
            value = self.AntiAliasingMode(value)
        self._set_element_value(self._get_anti_aliasing_element(), value.value)


    @property
    def disable_identify_relates(self):
        """Gets a boolean indicating whether or not displaying related information in identify results is enabled."""
        return self._value_to_boolean(
            self._get_element_value(
                self._get_disable_identify_relates_element()))

    @disable_identify_relates.setter
    def disable_identify_relates(self, value):
        value = self._value_to_boolean(value)
        self._set_element_value(
            self._get_disable_identify_relates_element(),
            value)


    @property
    def enable_dynamic_layers(self):
        """Gets a boolean value indicating whether or not dynamic layer order and symbology are enabled."""
        return self._value_to_boolean(
            self._get_element_value(
                self._get_enable_dynamic_layers_element()))

    @enable_dynamic_layers.setter
    def enable_dynamic_layers(self, value):
        """Gets a boolean value indicating whether or not dynamic layer order and symbology are enabled."""
        value = self._value_to_boolean(value)
        self._set_element_value(
            self._get_enable_dynamic_layers_element(),
            value)


    @property
    def feature_access_enabled_operations(self):
        """Gets a list of the enabled operations (by type name) that are currently enabled for the feature service."""
        values = self._get_enabled_feature_operations()
        # remove "Uploads" and "Editing" as these are internal operations not exposed in the ArcMap/Server UI.
        return [val for val in values if val not in {"Uploads","Editing"}]

    @feature_access_enabled_operations.setter
    def feature_access_enabled_operations(self, values):
        """Sets the operations (by an iterable of operation names) that are enabled for the feature service.

        Valid values are contained in the 'arcpyext.mapping.SDDraft.FeatureAccessOperation' enumerated type.
        Valid string values are:
         - 'Create'
         - 'Query'
         - 'Update'
         - 'Delete'
         - 'Sync'
        """
        string_values = []
        for val in values:
            if isinstance(val, basestring):
                #Convert all operation names to title case because that is what ArcMap outputs
                val = self.FeatureAccessOperation(val.title())
            elif not isinstance(val, self.FeatureAccessOperation):
                # not a known operation, raise exception
                raise TypeError("Operations list contains invalid operation types.")
            string_values.append(val.value)
            
        string_values = set(string_values)

        if [val for val in string_values if val in self._FEATURE_ACCESS_EDIT_OPERATIONS]:
            # If operation is in the _FEATURE_ACCESS_EDIT_OPERATIONS list, the "Uploads" and "Editing" operations
            # must also be enabled.  This functionality is hidden in the UI, but occurs when creating the service
            # definition draft in ArcMap.
            string_values.update({"Uploads","Editing"})
        self._set_enabled_feature_operations(string_values)


    @property
    def folder(self):
        """Gets the name of the folder that the service will reside in."""
        return super(SDDraft, self).folder

    @folder.setter
    def folder(self, value):
        """Sets the name of the folder that the service will reside in."""
        SDDraftBase.folder.fset(self, value)
        self._set_full_path_properties()


    @property
    def name(self):
        """Gets the name of the service."""
        return super(SDDraft, self).name

    @name.setter
    def name(self, value):
        """Sets the name of the service (Cannot be an empty value)."""
        SDDraftBase.name.fset(self, value)
        self._set_full_path_properties()


    @property
    def schema_locking_enabled(self):
        """Gets a boolean indicating whether or not the server locks the database schema."""
        return self._value_to_boolean(self._get_element_value(self._get_schema_locking_enabled_element()))

    @schema_locking_enabled.setter
    def schema_locking_enabled(self, value):
        """Sets a boolean indicating whether or not the server locks the database schema."""
        value = self._value_to_boolean(value)
        self._set_element_value(self._get_schema_locking_enabled_element(), value)


    @property
    def text_anti_aliasing_mode(self):
        """Gets the current anti-aliasing mode for map text."""
        return self.TextAntiAliasingMode(self._get_element_value(self._get_text_anti_aliasing_element()))

    @text_anti_aliasing_mode.setter
    def text_anti_aliasing_mode(self, value):
        """Sets the anti-aliasing mode for map graphics.

        Valid values are contained in the 'arcpyext.mapping.SDDraft.TextAntiAliasingMode' enumerated type.
        """
        if not isinstance(value, self.TextAntiAliasingMode):
            value = self.TextAntiAliasingMode(value)
        self._set_element_value(self._get_text_anti_aliasing_element(), value.value)

    ###################
    # PRIVATE METHODS #
    ###################

    # SDDraft XML Helpers
    def _get_anti_aliasing_element(self):
        return self._get_value_element_by_key(self._get_service_config_props(), "antialiasingMode")

    def _get_disable_identify_relates_element(self):
        return self._get_value_element_by_key(
            self._get_service_config_props(),
            "disableIdentifyRelates")

    def _get_enable_dynamic_layers_element(self):
        return self._get_value_element_by_key(
            self._get_service_config_props(),
            "enableDynamicLayers")

    def _get_enabled_feature_operations(self):
        ext_props = self._get_service_extension_by_type("FeatureServer").find("./Info/PropertyArray")
        enabled_ops_prop = self._get_value_element_by_key(ext_props, "WebCapabilities")
        return self._get_element_value(enabled_ops_prop).split(",")

    def _get_name_elements(self):
        base_elements = super(SDDraft, self)._get_name_elements()

        wcs_ext_props = self._get_service_extension_by_type("WCSServer").find("./Props/PropertyArray").findall("PropertySetProperty")
        wcs_ext_name_props = self._get_value_elements_by_keys(wcs_ext_props, ["name"])

        wfs_ext_props = self._get_service_extension_by_type("WFSServer").find("./Props/PropertyArray").findall("PropertySetProperty")
        wfs_ext_name_props = self._get_value_elements_by_keys(wfs_ext_props, ["name"])

        return base_elements + wcs_ext_name_props + wfs_ext_name_props

    def _get_schema_locking_enabled_element(self):
        return self._get_value_element_by_key(self._get_service_config_props(), "schemaLockingEnabled")

    def _get_service_extension_by_type(self, type_name):
        extensions = [item for item in self._get_elements_by_tag("SVCExtension") if item.findtext("TypeName") == type_name]
        return extensions[0] if len(extensions) == 1 else None

    def _get_text_anti_aliasing_element(self):
        return self._get_value_element_by_key(self._get_service_config_props(), "textAntialiasingMode")

    def _set_enabled_feature_operations(self, operations):
        ext_props = self._get_service_extension_by_type("FeatureServer").find("./Info/PropertyArray")
        enabled_ops_prop = self._get_value_element_by_key(ext_props, "WebCapabilities")
        self._set_element_value(enabled_ops_prop, ",".join([o.title() for o in operations]))

    def _set_full_path_properties(self):
        """Sets the value for properties that are dependent on both the folder name and the service name."""
        wfs_ext_props = self._get_service_extension_by_type("WFSServer").find("./Props/PropertyArray").findall("PropertySetProperty")
        wfs_ext_name_props = self._get_value_elements_by_keys(wfs_ext_props, ["appSchemaPrefix"])
        for prop in wfs_ext_name_props:
            merged_value = "{0}_{1}".format(self.folder, self.name) if self.folder != None else self.name
            self._set_element_value(prop, merged_value)