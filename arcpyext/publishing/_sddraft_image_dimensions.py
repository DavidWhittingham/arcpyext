# Python 2/3 compatibility
from __future__ import (absolute_import, division, print_function, unicode_literals)
from future.builtins import *
from future.builtins.disabled import *
from future.standard_library import install_aliases
install_aliases()

from ._sddraft_base import SDDraftBase

class SDDraftImageDimensions(SDDraftBase):

    @property
    def max_image_height(self):
        return self._editor.get_element_value(self._max_image_height_element)

    @max_image_height.setter
    def max_image_height(self, value):
        self._editor.set_element_value(
            self._max_image_height_element,
            self._editor.verify_int(value, "Maximum Download Height", allow_none = True))

    @property
    def max_image_width(self):
        return self._editor.get_element_value(self._max_image_width_element)

    @max_image_width.setter
    def max_image_width(self, value):
        self._editor.set_element_value(
            self._max_image_width_element,
            self._editor.verify_int(value, "Maximum Download Width", allow_none = True))

    @property
    def _max_image_height_element(self):
        return self._editor.get_value_element_by_key(self._config_props, "MaxImageHeight")

    @property
    def _max_image_width_element(self):
        return self._editor.get_value_element_by_key(self._config_props, "MaxImageWidth")