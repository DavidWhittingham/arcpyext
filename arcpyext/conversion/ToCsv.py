# coding=utf-8
"""Class for commonalities in the conversion process."""

# Python 2/3 compatibility
# pylint: disable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position
from __future__ import (absolute_import, division, print_function, unicode_literals)
from future.builtins.disabled import *
from future.builtins import *
from future.standard_library import install_aliases
install_aliases()
# pylint: enable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position

# Local imports
from ._ToCsvBase import ToCsvBase


class ToCsv(ToCsvBase):

    #region Public overrides

    def feature_class(self, input_fc, output_fc, use_field_alias_as_column_header=False):

        return super().feature_class(
            input_fc, output_fc, use_field_alias_as_column_header=use_field_alias_as_column_header
        )

    def table(self, input_table, output_table, use_field_alias_as_column_header=False):
        return super().table(
            input_table, output_table, use_field_alias_as_column_header=use_field_alias_as_column_header
        )

    def relationship_class(self, input_rel, output_rel):
        return super().relationship_class(input_rel, output_rel)

    def workspace(self, input_workspace, output_path, use_field_alias_as_column_header=False):
        return super().workspace(
            input_workspace, output_path, use_field_alias_as_column_header=use_field_alias_as_column_header
        )

    #endregion