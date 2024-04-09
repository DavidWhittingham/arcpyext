# coding=utf-8

# Python 2/3 compatibility
# pylint: disable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position,no-name-in-module,import-error
from __future__ import (absolute_import, division, print_function, unicode_literals)
from future.builtins.disabled import *
from future.builtins import *
from future.standard_library import install_aliases
install_aliases()
# pylint: enable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position,no-name-in-module,import-error

import os
import imp

import arcpy

import xml.etree.ElementTree as ET


class PythonToolbox(object):
    def __init__(self, toolbox_path):
        self.toolbox_path = toolbox_path

    def load(self):
        # let arcpy do it's convoluted thing - this generates the xml files if they didn't exist
        arcpy.ImportToolbox(self.toolbox_path)
        # and load the pyt file so that we can work with the actual objects (in this order, we get better exceptions if there are errors loading the module a second time)
        # this may not work if you can't import a module twice, eg. with Django Models, so may need to re-work your toolbox code to only import packages when necessary
        self.toolbox = imp.load_source('PythonToolbox', self.toolbox_path).Toolbox()
        self.tools = [PythonTool(self, t()) for t in self.toolbox.tools]

    @property
    def xml_path(self):
        return self.toolbox_path + '.xml'

    @classmethod
    def get_or_create_element(cls, element, name, attributes={}):
        xpath = name
        if attributes: xpath += '[' + ','.join(['@' + k + "='" + v + "'" for k, v in attributes.items()]) + ']'
        e = element.find(xpath)
        if e is None:
            e = ET.Element(name)
            for k, v in attributes.items():
                e.set(k, v)
            element.append(e)
        return e

    def apply_toolbox_descriptions(self):
        """Applies the description attributes on the Toolbox model to the xml sitting beside the toolbox file."""
        self.set_description_in_xml(self.toolbox.description)
        self.set_summary_in_xml(self.toolbox.summary)

        # and do tools too
        for t in self.tools:
            t.apply_tool_descriptions()

    def load_xml(self):
        self.xml_tree = ET.parse(self.xml_path)
        # and load tools too
        for t in self.tools:
            t.load_xml()

    def save_definitions(self):
        with open(self.xml_path, 'wb') as fout:
            self.xml_tree.write(fout, encoding='utf-8', xml_declaration=True)

        # and save tools too
        for t in self.tools:
            t.save_definitions()

    def set_description_in_xml(self, description):
        e = self.get_or_create_element(self.xml_tree.getroot(), 'dataIdInfo')
        e = self.get_or_create_element(e, 'idAbs')
        e.text = description

    def set_summary_in_xml(self, summary):
        e = self.get_or_create_element(self.xml_tree.getroot(), 'dataIdInfo')
        e = self.get_or_create_element(e, 'idAbs')
        e.text = summary


class PythonTool(object):
    def __init__(self, python_toolbox, tool):
        self.python_toolbox = python_toolbox
        self.tool = tool
        self.tool_name = self.tool.__class__.__name__

    @property
    def xml_path(self):
        return os.path.splitext(self.python_toolbox.toolbox_path)[0] + '.' + self.tool_name + '.pyt.xml'

    def apply_tool_descriptions(self):
        """Applies the description attributes on the Tool model to the xml sitting beside the toolbox file."""
        self.set_description_in_xml(self.tool.description)
        self.set_summary_in_xml(self.tool.summary)

        # and set parameter descriptions too
        for p in self.tool.getParameterInfo():
            if p.direction == 'Input':
                self.set_parameter_description_in_xml(p.name, p.description)

    def load_xml(self):
        self.xml_tree = ET.parse(self.xml_path)

    def save_definitions(self):
        with open(self.xml_path, 'wb') as fout:
            self.xml_tree.write(fout, encoding='utf-8', xml_declaration=True)

    def set_description_in_xml(self, description):
        e = PythonToolbox.get_or_create_element(self.xml_tree.getroot(), 'dataIdInfo')
        e = PythonToolbox.get_or_create_element(e, 'idAbs')
        e.text = description

    def set_parameter_description_in_xml(self, param_name, description):
        e = PythonToolbox.get_or_create_element(self.xml_tree.getroot(), 'tool', attributes={'name': self.tool_name})
        e = PythonToolbox.get_or_create_element(e, 'parameters')
        e = PythonToolbox.get_or_create_element(e, 'param', attributes={'name': param_name})
        e = PythonToolbox.get_or_create_element(e, 'dialogReference')
        e.text = description

    def set_summary_in_xml(self, summary):
        e = PythonToolbox.get_or_create_element(self.xml_tree.getroot(), 'tool', attributes={'name': self.tool_name})
        e = PythonToolbox.get_or_create_element(e, 'summary')
        e.text = summary
