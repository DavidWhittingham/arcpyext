import codecs
import xml.etree.ElementTree as ET
import xml.dom.minidom as DOM

class SDDraftEditor():
    """Class for containing the core functions for editing a Service Definition Draft document."""
    def __init__(self, path):
        self._path = path
        self._loadxml()

    #region Static Methods

    @staticmethod
    def append_element(parent_elem, subelem):
        """Adds a child element to the end of a parent element."""
        parent_elem.append(subelem)

    @classmethod
    def enum_list_to_str(cls, values, enum, exception_message):
        string_values = []
        for val in values:
            string_values.append(cls.enum_to_str(val, enum, exception_message))
        return ",".join(set(string_values))

    @classmethod
    def create_element(cls, tag, value, attrib = {}):
        elem = ET.Element(tag, attrib)
        cls.set_element_value(elem, value)
        return elem

    @classmethod
    def create_config_element(cls, key, value):
        key_elem = cls.create_element("Key", key)
        value_elem = cls.create_element("Value", value, {"xsi:type": "xs:string"})
        return cls.create_element(
            "PropertySetProperty", [key_elem, value_elem], {"xsi:type": "typens:PropertySetProperty"})

    @staticmethod
    def enum_to_str(value, enum, exception_message):
        if isinstance(value, basestring):
            # Convert string to enum to check compatibility
            # Raises ValueError if unknown value.
            value = enum(value)
        elif not isinstance(value, enum):
            # not a known capability, raise exception
            raise TypeError(exception_message)
        return value.value

    @staticmethod
    def get_element_value(element, default = None):
        if element.text == None:
            return default
        if element.text.upper() == "TRUE":
            return True
        if element.text.upper() == "FALSE":
            return False

        try:
            return int(element.text)
        except ValueError:
            pass

        try:
            return float(element.text)
        except (ValueError):
            pass

        return element.text

    @staticmethod
    def set_element_value(element, value):
        if value == None:
            element.text = None
            return
        if isinstance(value, bool):
            element.text = "true" if value == True else "false"
            return
        if isinstance(value, (int, float)):
            element.text = repr(value)
            return
        if isinstance(value, basestring):
            element.text = value
            return
        if isinstance(value, list):
            # assume list of elements, remove all current and set
            for elem in element:
                element.remove(elem)
            for elem in value:
                element.append(elem)
            return
        raise ValueError("Element value cannot be set, unknown type.")

    @classmethod
    def get_value_element_by_key(cls, prop_list, key):
        """ From a list of PropertySetProperty elements, return the "value" child element of the first
        PropertySetProperty element with a particular key."""
        for item in prop_list:
            if item.findtext("Key").lower() == key.lower():
                return item.find("Value")
        return None

    @staticmethod
    def get_value_elements_by_keys(prop_list, keys):
        """ From a list of PropertySetProperty elements, returns a list of the "value" child elements of
        PropertySetProperty elements with a particular key."""
        return [item.find("Value") for item in prop_list if item.findtext("Key") in keys]

    @staticmethod
    def value_to_boolean(value):
        """Converts true-ish and false-ish values to boolean."""
        try:
            value = value.upper()
            value = True if value in ["TRUE", "T"] else False
        except AttributeError:
            pass

        return value == True

    @classmethod
    def verify_float(self, value, name, allow_none = False, allow_negative = False, allow_zero = True):
        return self._verify_number(float, value, name, allow_none, allow_negative, allow_zero)

    @classmethod
    def verify_int(self, value, name, allow_none = False, allow_negative = False, allow_zero = True):
        return self._verify_number(int, value, name, allow_none, allow_negative, allow_zero)

    @staticmethod
    def _verify_number(type, value, name, allow_none, allow_negative, allow_zero):
        if value == None:
            if allow_none == False:
                raise ValueError("{0} cannot be None.".format(name))
            else:
                return None

        value = type(value)

        if allow_negative == False and value != None and value < 0:
            raise ValueError("{0} cannot be less than zero.".format(name))

        if allow_zero == False and value != None and value == 0:
            raise ValueError("{0} cannot be zero.".format(name))

        return value

    @staticmethod
    def _parse_xmlns(file):
        """Parses an XML file whilst preserving custom namespaces, which ElementTree doesn't do out of the box"""

        root = None
        ns_map = []

        for event, elem in ET.iterparse(file, ("start", "start-ns")):
            if event == "start-ns" and elem[0] != "xsi":
                # xsi is the only namespace supported out of the box, we don't need it twice so it is ignored
                ns_map.append(elem)
            elif event == "start":
                if root is None:
                    root = elem
                for prefix, uri in ns_map:
                    elem.set("xmlns:" + prefix, uri)
                ns_map = []

        return ET.ElementTree(root)

    #endregion

    #region Properties

    @property
    def xmlroot(self):
        return self._xmltree.getroot()

    @property
    def file_path(self):
        return self._path

    #endregion

    #region Methods

    def save(self):
        """Saves changes to the Service Definition Draft back to the file."""
        self.save_a_copy(self.file_path)

    def save_a_copy(self, path):
        """Saves a copy of the Service Definition Draft to a new file."""
        # ElementTree doesn't escape double quotes in element values where as the original SD Draft file from Esri does
        # Using Minidom because it escapes double quotes, just to be sure we're compatible

        xml_string = ET.tostring(self._xmltree.getroot())
        xml = DOM.parseString(xml_string.encode("utf-8"))
        f = codecs.open(path, 'w', "utf-8")
        xml.writexml(f, encoding = "utf-8")
        f.close()

    # Generic SD Draft Helpers
    def get_elements_by_tag(self, tag_name):
        return list(self.xmlroot.iter(tag_name))

    def get_first_element_by_tag(self, tag_name, root_element = None):
        if root_element == None:
            root_element = self.xmlroot
        return next(root_element.iter(tag_name))

    def _loadxml(self):
        self._xmltree = self._parse_xmlns(self._path)

    #endregion