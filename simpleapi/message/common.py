# -*- coding: utf-8 -*-

try:
    import json
except ImportError:
    try:
        from django.utils import simplejson as json
    except Exception, e:
        import simplejson as json

__all__ = ('json', 'SAException')

class SAException(Exception):
    def __init__(self, msg=None):
        self._message = msg
        super(Exception, self).__init__(self)

    def _get_message(self):
        return self._message

    def _set_message(self, message):
        self._message = message

    message = property(_get_message, _set_message)