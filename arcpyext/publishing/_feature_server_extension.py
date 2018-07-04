from __future__ import (absolute_import, division, print_function, unicode_literals)
from builtins import (ascii, bytes, chr, dict, filter, hex, input, int, map, next, oct, open, pow,
                      range, round, str, super, zip)

from ._sddraft_extension import SDDraftExtension

from enum import Enum


class FeatureServerExtension(SDDraftExtension):

    class Capability(Enum):
        create = "Create"
        delete = "Delete"
        extract = "Extract"
        query = "Query"
        sync = "Sync"
        update = "Update"

    _ALLOW_GEOMETRY_UPDATES_KEY = "allowGeometryUpdates"
    _ALLOW_OTHERS_TO_DELETE_KEY = "allowOthersToDelete"
    _ALLOW_OTHERS_TO_QUERY_KEY = "allowOthersToQuery"
    _ALLOW_OTHERS_TO_UPDATE_KEY = "allowOthersToUpdate"
    _ALLOW_TRUE_CURVES_UPDATES_KEY = "allowTrueCurvesUpdates"
    _ENABLE_OWNERSHIP_BASED_ACCESS_CONTROL_KEY = "enableOwnershipBasedAccessControl"
    _ENABLE_Z_DEFAULTS_KEY = "enableZDefaults"
    _EXTENSION_TYPE = "FeatureServer"
    _FEATURE_ACCESS_EDIT_OPERATIONS = ["Create", "Delete", "Update"]
    _MAX_RECORD_COUNT_KEY = "maxRecordCount"
    _REALM_KEY = "realm"
    _Z_DEFAULT_VALUE_KEY = "zDefaultValue"

    @property
    def allow_geometry_updates(self):
        """Gets or sets a value to enable or disable the ability to update geometry.

        :type: bool
        """
        return self._get_prop_value(self._ALLOW_GEOMETRY_UPDATES_KEY)

    @allow_geometry_updates.setter
    def allow_geometry_updates(self, value):
        self._set_prop_value(self._ALLOW_GEOMETRY_UPDATES_KEY, self._editor.value_to_boolean(value))

    @property
    def allow_others_to_delete(self):
        """Gets or sets a value to enable or disable the ability of individuals to delete features owned by other users.

        :type: bool
        """
        return self._get_prop_value(self._ALLOW_OTHERS_TO_DELETE_KEY)

    @allow_others_to_delete.setter
    def allow_others_to_delete(self, value):
        self._set_prop_value(self._ALLOW_OTHERS_TO_DELETE_KEY, self._editor.value_to_boolean(value))

    @property
    def allow_others_to_query(self):
        """Gets or sets a value to enable or disable the ability of individuals to query features owned by other users.

        :type: bool
        """
        return self._get_prop_value(self._ALLOW_OTHERS_TO_QUERY_KEY)

    @allow_others_to_query.setter
    def allow_others_to_query(self, value):
        self._set_prop_value(self._ALLOW_OTHERS_TO_QUERY_KEY, self._editor.value_to_boolean(value))

    @property
    def allow_others_to_update(self):
        """Gets or sets a value to enable or disable the ability of individuals to update features owned by other users.

        :type: bool
        """
        return self._get_prop_value(self._ALLOW_OTHERS_TO_UPDATE_KEY)

    @allow_others_to_update.setter
    def allow_others_to_update(self, value):
        self._set_prop_value(self._ALLOW_OTHERS_TO_UPDATE_KEY, self._editor.value_to_boolean(value))

    @property
    def allow_true_curves_updates(self):
        """Gets or sets a value to enable or disable the ability to update geometry using true curves.

        :type: bool
        """
        return self._get_prop_value(self._ALLOW_TRUE_CURVES_UPDATES_KEY)

    @allow_true_curves_updates.setter
    def allow_true_curves_updates(self, value):
        self._set_prop_value(self._ALLOW_TRUE_CURVES_UPDATES_KEY, self._editor.value_to_boolean(value))

    @property
    def capabilities(self):
        """Gets a list of the enabled operations (by type name) that are currently enabled for the feature service."""
        # remove "Uploads" and "Editing" as these are internal operations not exposed in the ArcMap/Server UI.
        return [self.Capability(item) for item in self._editor.get_element_value(self._capabilities_element).split(",")
            if item not in ("Uploads", "Editing")]

    @capabilities.setter
    def capabilities(self, values):
        """Sets the operations (by an iterable of operation names) that are enabled for the feature service.

        :type: self.Capability
        """
        values = set([self._editor.enum_to_str(val, self.Capability, "capability") for val in values])
        if [val for val in values if val in self._FEATURE_ACCESS_EDIT_OPERATIONS]:
            # If operation is in the _FEATURE_ACCESS_EDIT_OPERATIONS list, the "Uploads" and "Editing" operations
            # must also be enabled.  This functionality is hidden in the UI, but occurs when creating the service
            # definition draft in ArcMap.
            values.update(["Uploads", "Editing"])

        self._editor.set_element_value(self._capabilities_element, ",".join(values))

    @property
    def enable_ownership_based_access_control(self):
        """Gets or sets a value to enable or disable ownership-based access control for feature editing.

        :type: bool
        """
        return self._get_prop_value(self._ENABLE_OWNERSHIP_BASED_ACCESS_CONTROL_KEY)

    @enable_ownership_based_access_control.setter
    def enable_ownership_based_access_control(self, value):
        self._set_prop_value(self._ENABLE_OWNERSHIP_BASED_ACCESS_CONTROL_KEY, self._editor.value_to_boolean(value))

    @property
    def enable_z_defaults(self):
        """Gets or sets a value indicating whether or not features with Z-values should be enabled for editing.

        :type: bool
        """
        return self._get_prop_value(self._ENABLE_Z_DEFAULTS_KEY)

    @enable_z_defaults.setter
    def enable_z_defaults(self, value):
        self._set_prop_value(self._ENABLE_Z_DEFAULTS_KEY, self._editor.value_to_boolean(value))

    @property
    def max_record_count(self):
        """Gets or sets the maximum record count that can be returned by the service.

        :type: int
        """
        return self._get_prop_value(self._MAX_RECORD_COUNT_KEY)

    @max_record_count.setter
    def max_record_count(self, value):
        self._set_prop_value(
            self._MAX_RECORD_COUNT_KEY,
            self._editor.verify_int(value, "max. record count"))

    @property
    def realm(self):
        """Gets or sets the realm to be added to a user name when applying edits (username@realm).

        :type: str
        """
        return self._get_prop_value(self._REALM_KEY)

    @realm.setter
    def realm(self, value):
        self._set_prop_value(self._REALM_KEY, value)

    @property
    def z_default_value(self):
        """Gets or sets the maximum record count that can be returned by the service.

        :type: float
        """
        return self._get_prop_value(self._Z_DEFAULT_VALUE_KEY)

    @z_default_value.setter
    def z_default_value(self, value):
        self._set_prop_value(
            self._Z_DEFAULT_VALUE_KEY,
            self._editor.verify_float(value, "Z default value"))