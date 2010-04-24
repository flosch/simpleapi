# -*- coding: utf-8 -*-

try:
    import json
except ImportError:
    import simplejson as json

__all__ = ('__formatters__',)

class Formatter(object):
    
    def __init__(self, http_request, callback):
        self.http_request = http_request
        self.callback = callback
    
    def build(self, value):
        raise NotImplemented
    
    def parse(self, value):
        raise NotImplemented

class JSONFormatter(Formatter):
    
    __mime__ = "application/json"
    
    def build(self, value):
        return json.dumps(value)
    
    def parse(self, value):
        return json.loads(value)

class JSONPType(Formatter):
    
    __mime__ = "application/javascript"
    
    def build(self, value):
        return u'%s(%s)' % (self.callback or 'simpleapiCallback', json.dumps(data))
    
    def parse(self, value):
        return json.loads(value)

class ValueFormatter(Formatter):
    
    def build(self, value):
        return value
    
    def parse(self, value):
        return unicode(value)

__formatters__ = {
    'json': JSONFormatter,
    'value': ValueFormatter
}