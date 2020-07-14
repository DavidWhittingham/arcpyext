# coding=utf-8


class CimEditor(object):
    def __init__(self, arcpy_obj, cim_version="V2"):
        self._arcpy_obj = arcpy_obj
        self._cim_obj = self._arcpy_obj.getDefinition(cim_version)

    def __enter__(self):
        return self._cim_obj

    def __exit__(self, ex_type, ex_value, traceback):
        if ex_type == None:
            self._arcpy_obj.setDefinition(self._cim_obj)