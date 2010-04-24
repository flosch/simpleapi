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

class JSONPFormatter(Formatter):
    __mime__ = "application/javascript"
    
    def build(self, value):
        func = self.callback or 'simpleapiCallback'
        return u'{func}({data})'.format(func=func, data=json.dumps(value))
    
    def parse(self, value):
        return json.loads(value)

class ValueFormatter(Formatter):
    __mime__ = "text/html"
    
    def build(self, value):
        return value
    
    def parse(self, value):
        return unicode(value)

__formatters__ = {
    'json': JSONFormatter,
    'jsonp': JSONPFormatter,
    'value': ValueFormatter
}