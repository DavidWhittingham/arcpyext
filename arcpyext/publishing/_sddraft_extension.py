# Python 2/3 compatibility
from __future__ import (absolute_import, division, print_function, unicode_literals)
from future.builtins import *
from future.builtins.disabled import *
from future.standard_library import install_aliases
install_aliases()

from abc import ABCMeta
from enum import Enum


class SDDraftExtension():
    __metaclass__ = ABCMeta

    class Capability(Enum):
        """Must be overridden by sub-classes if any capabilities are supported."""
        pass

    # region Constants

    #: Name of the extension type as used in the SD Draft XML document.
    #: This must be overridden by implementers.
    _EXTENSION_TYPE = None

    #: Key for capabilities of the extension.
    #: Should be the same for all extensions, but can be overridden by implementers.
    _CAPABILITIES_KEY = "WebCapabilities"

    # endregion

    # region Variables

    #: SDDraftEditor object.  Available to implementers for editing the SD Draft XML.
    _editor = None

    # endregion

    # region Constructor(s)

    def __init__(self, editor):
        """Initialises a new instance of this class.

        :param editor: A SDraftEditor object for applying property changes to the XML document.
        :type editor: arcpyext.publishing.SDDraftEditor

        """
        self._editor = editor

    # endregion

    # region Properties

    @property
    def capabilities(self):
        """Gets or sets a list of capabilities (as defined by the self.Capability enumerator)
        that are enabled for this extension.

        :type: list(self.Capability)
        """
        value = self._editor.get_element_value(self._capabilities_element)
        if value != None and value != "":
            return [self.Capability(val) for val in value.split(",")]
        else:
            return []

    @capabilities.setter
    def capabilities(self, values):
        self._editor.set_element_value(
            self._capabilities_element,
            self._editor.enum_list_to_str(values, self.Capability, "Capabilities list contains invalid capability."),
            True,
            True)

    @property
    def enabled(self):
        """Gets or sets a boolean value that describes if the extension is enabled.

        :type: bool
        """
        return self._editor.value_to_boolean(
            self._editor.get_element_value(
                self._extension_config.find("Enabled")))

    @enabled.setter
    def enabled(self, value):
        self._editor.set_element_value(
            self._extension_config.find("Enabled"), self._editor.value_to_boolean(value))

    @property
    def _extension_config(self):
        """Gets the XML configuration object for the extension, based on _EXTENSION_TYPE."""
        return next(item for item in self._editor.get_elements_by_tag("SVCExtension")
            if item.findtext("TypeName") == self._EXTENSION_TYPE)

    @property
    def _capabilities_element(self):
        """Gets the capabilities element of the extension configuration."""
        return self._editor.get_value_element_by_key(self._extension_info, self._CAPABILITIES_KEY)

    @property
    def _extension_info(self):
        """Gets an iterable PropertyArray of PropertySetProperty elements for the extension's info element."""
        return self._extension_config.find("./Info/PropertyArray")

    @property
    def _extension_properties(self):
        """Gets an iterable PropertyArray of PropertySetProperty elements for the extension's props element."""
        return self._extension_config.find("./Props/PropertyArray")

    # endregion

    # region Methods

    def _set_props_from_dict(self, prop_dict):
        """Method for setting properties from a dictionary where keys match property names.

        Can be overridden by sub-classes.
        """
        for k, v in prop_dict.items():
            if hasattr(self, k):
                setattr(self, k, v)

    def _get_prop_value(self, key):
        """Gets the value for a given extension 'props' property."""
        elem = self._editor.get_value_element_by_key(self._extension_properties, key)
        return None if elem == None else self._editor.get_element_value(elem)

    def _set_prop_value(self, key, value):
        """Sets the value for a given extension 'props' property."""
        elem = self._editor.get_value_element_by_key(self._extension_properties, key)
        if elem == None:
            # element doesn't exist, presume caller knows what they're doing and create the property
            self._editor.append_element(
                self._extension_properties,
                self._editor.create_config_element(key, value))
        else:
            self._editor.set_element_value(
                self._editor.get_value_element_by_key(self._extension_properties, key), value)

    # endregion