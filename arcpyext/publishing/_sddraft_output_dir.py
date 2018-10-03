from __future__ import (absolute_import, division, print_function, unicode_literals)
from builtins import (bytes, dict, int, list, object, range, str, ascii, chr, hex, input, next, oct, open, pow, round,
                      super, filter, map, zip)

from ._sddraft_base import SDDraftBase

class SDDraftOutputDirMixin(SDDraftBase):

    _OUTPUT_DIR_KEY = "outputDir"
    _VIRTUAL_OUTPUT_DIR_KEY = "virtualOutputDir"

    @property
    def output_dir(self):
        """Gets the output directory for the service."""
        output_dir_element = self._output_dir_element
        if not output_dir_element:
            return None

        return self._editor.get_element_value(output_dir_element)

    @output_dir.setter
    def output_dir(self, value):
        """Sets the output directory for the service.  This is paired with the virtual output directory property."""
        output_dir_element = self._output_dir_element
        if not output_dir_element:
            # Create an outputDir element and append it to the configuration properties
            self._editor.append_element(
                self._config_props,
                self._editor.create_config_element(self._OUTPUT_DIR_KEY, value))
        else:
            self._editor.set_element_value(output_dir_element, value)

    @property
    def virtual_output_dir(self):
        """Gets the virtual output directory for the service."""
        virtual_output_dir_element = self._virtual_output_dir_element
        if not virtual_output_dir_element:
            return None

        return self._editor.get_element_value(virtual_output_dir_element)

    @virtual_output_dir.setter
    def virtual_output_dir(self, value):
        """Sets the virtual output directory for the service.  This is paired with the output directory property."""
        virtual_output_dir_element = self._virtual_output_dir_element
        if not virtual_output_dir_element:
            # Create a virtualOutputDir element and append it to the configuration properties
            self._editor.append_element(
                self._config_props,
                self._editor.create_config_element(self._VIRTUAL_OUTPUT_DIR_KEY, value))
        else:
            self._editor.set_element_value(virtual_output_dir_element, value)

    @property
    def _output_dir_element(self):
        self._editor.get_value_element_by_key(self._config_props, self._OUTPUT_DIR_KEY)

    @property
    def _virtual_output_dir_element(self):
        self._editor.get_value_element_by_key(self._config_props, self._VIRTUAL_OUTPUT_DIR_KEY)