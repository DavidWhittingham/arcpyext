from .arc_py_ext_error import ArcPyExtError

class ChangeDataSourcesError(ArcPyExtError):
    """description of class"""

    def __init__(self, message, errors = None):
        super(ChangeDataSourcesError, self).__init__(message)
        self._errors = errors

    @property
    def errors(self):
        return self._errors