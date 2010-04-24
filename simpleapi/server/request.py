# -*- coding: utf-8 -*-

from response import Response
from formatter import __formatters__

__all__ = ('Request', 'RequestException')

class RequestException(Exception): pass 
class Request(object):
    
    def __init__(self, http_request, namespace):
        self.http_request = http_request
        self.namespace = namespace
    
    def run(self):
        request_items = dict(self.http_request.REQUEST.items())
        
        # set all required simpleapi arguments
        mimetype = request_items.pop('_mimetype', None)
        callback = request_items.pop('_callback', None)
        access_key = request_items.pop('_access_key', None)
        output_formatter = request_items.pop('_output', None)
        input_formatter = request_items.pop('_input', 'value')
        method = request_items.pop('_call', None)
        
        # check whether method exists
        if not self.namespace['functions'].has_key(method):
            raise RequestException(u'Method %s does not exist.' % method)
        
        # get input formatter
        if input_formatter not in __formatters__:
            raise RequestException(u'Unkonwn input formatter: ' % input_formatter)
        input_formatter = __formatters__[input_formatter]
        
        # get output formatter
        if output_formatter not in __formatters__:
            raise RequestException(u'Unkonwn output formatter: ' % output_formatter)
        output_formatter = __formatters__[output_formatter]
        
        # check authentication
        if not self.namespace['authentication'](access_key):
            raise RequestException(u'Authentication failed.')
        
        # check ip address
        if not self.namespace['ip_restriction'](self.http_request.META.get('REMOTE_ADDR')):
            raise RequestException(u'You are not allowed to access.')
        
        # check all required arguments
        
        # make the call
        
        
        return Response(
            mimetype=mimetype
        )