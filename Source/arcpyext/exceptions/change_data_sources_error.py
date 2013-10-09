from .arc_py_ext_error import ArcPyExtError

class ChangeDataSourcesError(ArcPyExtError):
    """description of class"""

    def __init__(self, *args, **kwargs):

        self.errors = kwargs.pop("errors", None)

        return super(ChangeDataSourcesError, self).__init__(*args, **kwargs)