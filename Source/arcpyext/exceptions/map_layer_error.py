from .arc_py_ext_error import ArcPyExtError

class MapLayerError(ArcPyExtError):
    """description of class"""

    def __init__(self, *args, **kwargs):

        self.layer = kwargs.pop("layer", None)

        return super(MapLayerError, self).__init__(*args, **kwargs)