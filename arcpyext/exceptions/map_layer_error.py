from .arc_py_ext_error import ArcPyExtError

class MapLayerError(ArcPyExtError):
    """ArcPyExt exception for errors involving map layers."""

    def __init__(self, message, layer, innerError = None):
        super(MapLayerError, self).__init__(message, innerError)
        self._layer = layer
        
    @property
    def layer(self):
        return self._layer