from .map_layer_error import MapLayerError

class DataSourceUpdateError(MapLayerError):
    """Error raised when a datasource fails to change for a given layer."""
    pass