# -*- coding: utf-8 -*-

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
        input_formatter = request_items.pop('_input', None)
        method = request_items.pop('_call', None)
        
        # check whether method exists
        if not self.namespace['functions'].has_key(method):
            raise RequestException(u'Method %s does not exist.' % method)
        
        