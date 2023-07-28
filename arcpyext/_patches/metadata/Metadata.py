# coding=utf-8
"""
This module contains patches to Esri's *arcpy.metadata.Metadata* class.  These patches may insert functionality or fix 
issues directly in the *arcpy.metadata.Metadata* class.
"""
import collections.abc
import re

import arcpy

from lxml import etree as ET

from ...TopicCategory import TopicCategory

TOPIC_CATEGORIES_DISPLAY_NAME_TO_ENUM = {e.display_name.lower(): e for e in TopicCategory}
TOPIC_CATEGORIES_STANDARD_NAME_TO_ENUM = {e.standard_name.lower(): e for e in TopicCategory}
TOPIC_CATEGORIES_PORTAL_NAME_TO_ENUM = {e.portal_name.lower(): e for e in TopicCategory}


def _str_to_topic_category(value):
    try:
        return TopicCategory(value)
    except ValueError:
        # not a valid input for the enum, try parsing text values
        if not isinstance(value, str):
            raise

        value = value.lower()
        for str_dict in [
            TOPIC_CATEGORIES_DISPLAY_NAME_TO_ENUM, TOPIC_CATEGORIES_STANDARD_NAME_TO_ENUM,
            TOPIC_CATEGORIES_PORTAL_NAME_TO_ENUM
        ]:
            enum_val = str_dict.get(value)
            if enum_val:
                return enum_val

        # didn't find enum value based on string input either, re-raise ValueError
        raise


def add_topicCategories():
    def topicCategories_getter(self):
        metadata_xml = self.xml

        if not metadata_xml:
            # no XML, not supported, raise error
            raise NotImplementedError("Metadata object currently has none or empty XML.")

        metadata_xml_tree = ET.ElementTree(ET.fromstring(metadata_xml))
        topic_categories_xpath = "/metadata[@xml:lang=\"en\"]/dataIdInfo/tpCat/TopicCatCd"

        # get a list of topic elements
        topic_category_elements = metadata_xml_tree.xpath(topic_categories_xpath)

        if not topic_category_elements:
            # no elmeents found, return empty list
            return []

        # convert each element value to a str
        return [TopicCategory(value) for value in [e.attrib["value"] for e in topic_category_elements]]

    def topicCategories_setter(self, value):
        metadata_xml = self.xml

        if not metadata_xml:
            # no XML, not supported, raise error
            raise NotImplementedError("Metadata object currently has none or empty XML.")

        # process value into elements
        if isinstance(value, str):
            # presume we were supplied a one or more topic categorie as a string, delimited
            value = [s.strip() for s in re.split(",|;", value)]
        elif isinstance(value, TopicCategory):
            # a single enumerated type has been given, put in a list
            value = [value]

        if value is None:
            # value is none, make an empty list
            value = []
        elif not isinstance(value, collections.abc.Sequence):
            raise ValueError("Input 'topicCategories' value is not valid.")

        # value is now a sequence presumeably of either an enumerated type already, or a string representing the
        # display name, the ISO name, or portal name.
        # attempt to resolve each sequence value to an enum and then create element
        value = [ET.Element("TopicCatCd", value=_str_to_topic_category(v).value) for v in value]

        # set elements in XML
        topic_categories_parent_xpath = "/metadata[@xml:lang=\"en\"]/dataIdInfo/tpCat"
        metadata_xml_tree = ET.ElementTree(ET.fromstring(metadata_xml))
        topic_category_parent_element = next(iter(metadata_xml_tree.xpath(topic_categories_parent_xpath)), None)
        topic_category_parent_element.clear()
        topic_category_parent_element.extend(value)

        # save XML back to arcpy
        self.xml = ET.tostring(metadata_xml_tree.getroot(), encoding="utf-8", pretty_print=False)

    topicCategories_prop = property(topicCategories_getter, topicCategories_setter)

    if hasattr(arcpy.metadata.Metadata, "topicCategories"):
        # Esri have added a topicCategories property, bail out
        return

    # patch arcpy
    arcpy.metadata.Metadata.topicCategories = topicCategories_prop


add_topicCategories()