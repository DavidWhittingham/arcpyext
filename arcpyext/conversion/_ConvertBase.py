# coding=utf-8
"""Base class for commonalities in the conversion process."""

# Python 2/3 compatibility
# pylint: disable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position
from __future__ import (absolute_import, division, print_function, unicode_literals)
from future.builtins.disabled import *
from future.builtins import *
from future.standard_library import install_aliases
from future.utils import with_metaclass
install_aliases()
# pylint: enable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position

# Standard library imports
from abc import ABCMeta as _ABCMeta, abstractmethod

# Third-party imports
import arcpy

from pathlib2 import Path


class ConvertBase(with_metaclass(_ABCMeta, object)):
    def feature_class(self, input_fc, output_fc, **kwargs):
        if not arcpy.Exists(input_fc):
            raise ValueError("input_fc does not exist.")

        if arcpy.Exists(output_fc):
            raise ValueError("output_fc already exists.")

        # get input feature class description for copy process
        input_fc_desc = arcpy.Describe(input_fc)

        if not input_fc_desc.dataType == "FeatureClass":
            raise ValueError("input_fc is not of type 'FeatureClass'.")

        output_fc = Path(output_fc).resolve()

        self._feature_class(input_fc_desc, output_fc, **kwargs)

        del input_fc_desc
        arcpy.management.ClearWorkspaceCache()

    def table(self, input_table, output_table, **kwargs):
        if not arcpy.Exists(input_table):
            raise ValueError("input_table does not exist.")

        if arcpy.Exists(output_table):
            raise ValueError("output_table already exists.")

        # get input feature class description for copy process
        input_table_desc = arcpy.Describe(input_table)

        if not input_table_desc.dataType == "Table":
            raise ValueError("input_table is not of type 'Table'.")

        output_table = Path(output_table).resolve()

        self._table(input_table_desc, output_table, **kwargs)

        del input_table_desc
        arcpy.management.ClearWorkspaceCache()

    def relationship_class(self, input_rel, output_rel, **kwargs):
        if not arcpy.Exists(input_rel):
            raise ValueError("input_rel does not exist.")

        if arcpy.Exists(input_rel):
            raise ValueError("output_rel already exists.")

        # get input feature class description for copy process
        rel_class_desc = arcpy.Describe(input_rel)

        if not rel_class_desc.dataType == "RelationshipClass":
            raise ValueError("input_rel is not of type 'RelationshipClass'.")

        output_rel = Path(output_rel).resolve()

        self._relationship_class(rel_class_desc, output_rel, **kwargs)

        del rel_class_desc
        arcpy.management.ClearWorkspaceCache()

    def workspace(self, input_workspace, output_path, **kwargs):
        if not arcpy.Exists(input_workspace):
            raise ValueError("input_workspace does not exist.")

        workspace_desc = arcpy.Describe(input_workspace)

        if not workspace_desc.dataType == "Workspace":
            raise ValueError("input_workspace is not of type 'Workspace'.")

        # get output_path as a Path object
        output_path = Path(output_path).resolve()

        self._create_output_workspace(output_path, **kwargs)

        for child in workspace_desc.children:
            if child.dataType == 'FeatureClass':
                self._feature_class(child, self._feature_class_default_name(child, output_path, **kwargs), **kwargs)
            elif child.dataType == 'Table':
                self._table(child, self._table_default_name(child, output_path, **kwargs), **kwargs)
            elif child.dataType == 'RelationshipClass':
                self._relationship_class(
                    child, self._relationship_class_default_name(child, output_path, **kwargs), **kwargs
                )

        del workspace_desc
        arcpy.management.ClearWorkspaceCache()

    @abstractmethod
    def _create_output_workspace(self, output_path, **kwargs):
        return

    @abstractmethod
    def _feature_class(self, desc, output_fc, **kwargs):
        return

    @abstractmethod
    def _feature_class_default_name(self, desc, output_workspace, **kwargs):
        """
        Creates a Path object representing the full path of an output feature class in whatever the destination format is.
        """
        return

    @abstractmethod
    def _table(self, desc, output_table, **kwargs):
        return

    @abstractmethod
    def _table_default_name(self, desc, output_workspace, **kwargs):
        """
        Creates a Path object representing the full path of an output feature class in whatever the destination format is.
        """
        return

    def _relationship_class(self, desc, output_rel, **kwargs):
        """
        Basic/fallback text output relationship export that details the relationship information.
        """

        # NOTE: originClassKeys only available in 10.2.1+; only tested with a simple relate
        origin_classes = ', '.join(desc.originClassNames)
        destination_classes = ', '.join(desc.destinationClassNames)
        primary_keys = ', '.join([f[0] for f in desc.originClassKeys if f[1] == 'OriginPrimary'])
        foreign_keys = ', '.join([f[0] for f in desc.originClassKeys if f[1] == 'OriginForeign'])
        with output_rel.open('w') as fout:
            fout.write(u'RelationshipClass: {}\n'.format(desc.name))
            fout.write(u'From: {} ({})\n'.format(origin_classes, primary_keys))
            fout.write(u'To: {} ({})\n'.format(destination_classes, foreign_keys))

    def _relationship_class_default_name(self, desc, output_workspace, **kwargs):
        """
        Creates a Path object representing the full path of an output feature class in whatever the destination format is.
        """
        return output_workspace.joinpath(desc.name + ".txt")
