# -*- coding: utf-8 -*-

from django.http import HttpResponse

from formatter import __formatters__
from wrapper import __wrappers__

__all__ = ('Response', 'ResponseException')

class ResponseException(object): pass
class Response(object):
    
    def __init__(self, http_request, output_formatter=None, wrapper=None, 
                 errors=None, result=None, mimetype=None, callback=None):
        self.http_request = http_request
        self.errors = errors
        self.result = result
        self.mimetype = mimetype
        self.callback = None
        
        if wrapper:
            if isinstance(wrapper, type):
                self.wrapper = wrapper(errors, result)
            else:
                self.wrapper = wrapper
        else:
            self.wrapper = __wrappers__['default'](errors, result)
        
        if output_formatter:
            if isinstance(output_formatter, type):
                self.output_formatter = output_formatter(
                    http_request=http_request,
                    callback=callback                    
                )
            else:
                self.output_formatter = output_formatter
        else:
            self.output_formatter = __formatters__['json'](
                http_request=http_request,
                callback=callback
            )
        
        self.mimetype = mimetype or self.output_formatter.__mime__
    
    def build(self):
        wrapper_result = self.wrapper.build()
        formatter_result = self.output_formatter.build(wrapper_result)
        
        return HttpResponse(
            formatter_result,
            mimetype=self.mimetype
        )