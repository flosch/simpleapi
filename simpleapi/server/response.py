# -*- coding: utf-8 -*-

from django.http import HttpResponse

from formatter import __formatters__
from wrapper import __wrappers__

__all__ = ('Response', 'ResponseException')

class ResponseException(object): pass
class Response(object):
    
    def __init__(self, output_formatter=None, wrapper=None, errors=None,
                 result=None, mimetype='text/html'):
        self.errors = errors
        self.result = result
        self.mimetype = mimetype
        
        self.output_formatter = output_formatter or __formatters__['json']
        self.wrapper = wrapper or __wrappers__['default']
    
    def build(self):
        return HttpResponse(
            'huhu',
            mimetype=self.mimetype
        )