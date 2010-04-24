# -*- coding: utf-8 -*-

from django.http import HttpResponse

__all__ = ('Response', 'ResponseException')

class ResponseException(object): pass
class Response(object):
    
    def __init__(self, errors=None, result=None):
        self.errors = errors
        self.result = result
    
    def build(self, wrapper=None, output_formatter=None):
        return HttpResponse(
            'huhu'
        )