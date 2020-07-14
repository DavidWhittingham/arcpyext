# coding=utf-8


class Field(object):

    _fieldName = None
    _alias = None
    _visible = None

    def __init__(self, fieldName, alias, visible):
        self._fieldName = fieldName
        self._alias = alias
        self._visible = visible

    @property
    def alias(self):
        return self._alias

    @property
    def fieldName(self):
        return self._fieldName

    @property
    def visible(self):
        return self._visible
