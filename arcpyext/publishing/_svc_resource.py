class SVCResource(object):

    _ON_PREMISE_PATH_KEY = "OnPremisePath"
    _ID_KEY = "ID"

    def __init__(self, editor, elem):
        self._editor = editor
        self._resource_elem = elem
    
    @property
    def id(self):
        """Gets or sets the path to the ID for the service.

        :type: str
        """
        return self._get_prop_value(self._ID_KEY)

    @property
    def on_premise_path(self):
        """Gets or sets the path to the input for the service definition draft.

        :type: str
        """
        return self._get_prop_value(self._ON_PREMISE_PATH_KEY)

    @on_premise_path.setter
    def on_premise_path(self, value):
        self._set_prop_value(self._ON_PREMISE_PATH_KEY, value)

    def _get_prop_value(self, tag):
        """Gets the value for a given resource property."""
        return self._editor.get_element_value(self._editor.get_first_element_by_tag(tag, self._resource_elem))

    def _set_prop_value(self, tag, value):
        """Sets the value for a given resource property."""
        self._editor.set_element_value(self._editor.get_first_element_by_tag(tag, self._resource_elem), value)