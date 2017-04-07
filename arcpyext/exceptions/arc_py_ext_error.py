class ArcPyExtError(Exception):
    """Base error class for all ArcPyExt errors."""
    
    def __init__(self, message, innerError = None):
        super(ArcPyExtError, self).__init__(message)
        self._innerError = innerError
       
    @property
    def innerError(self):
        return self._innerError