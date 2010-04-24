# -*- coding: utf-8 -*-

from response import Response
from formatter import __formatters__
from wrapper import __wrappers__
from session import Session

__all__ = ('Request', 'RequestException')

class RequestException(Exception): pass 
class Request(object):
    
    def __init__(self, http_request, namespace):
        self.http_request = http_request
        self.namespace = namespace
        self.session = Session(request=http_request)
    
    def run(self):
        request_items = dict(self.http_request.REQUEST.items())
        
        # set all required simpleapi arguments
        mimetype = request_items.pop('_mimetype', None)
        callback = request_items.pop('_callback', None)
        access_key = request_items.pop('_access_key', None)
        output_formatter = request_items.pop('_output', 'json')
        input_formatter = request_items.pop('_input', 'value')
        method = request_items.pop('_call', None)
        wrapper = request_items.pop('_wrapper', 'default')
        version = request_items.pop('_version', 'default')
        
        # update session
        self.session.mimetype = mimetype
        self.session.callback = callback
        self.session.access_key = access_key
        
        # instantiate namespace
        local_namespace = self.namespace['class'](self)
        
        # check whether method exists
        if not self.namespace['functions'].has_key(method):
            raise RequestException(u'Method %s does not exist.' % method)
        
        # get input formatter
        if input_formatter not in __formatters__:
            raise RequestException(u'Unkonwn input formatter: %s' % input_formatter)
        input_formatter = __formatters__[input_formatter](self.http_request, callback)
        
        # get output formatter
        if output_formatter not in __formatters__:
            raise RequestException(u'Unkonwn output formatter: %s' % output_formatter)
        output_formatter = __formatters__[output_formatter](self.http_request, callback)
        
        # get wrapper
        if wrapper not in __wrappers__:
            raise RequestException(u'Unkonwn wrapper: %s' % wrapper)
        wrapper = __wrappers__[wrapper]
        
        # check authentication
        if not self.namespace['authentication'](local_namespace, access_key):
            raise RequestException(u'Authentication failed.')
        
        # check ip address
        if not self.namespace['ip_restriction'](local_namespace, \
                                                self.http_request.META.get('REMOTE_ADDR')):
            raise RequestException(u'You are not allowed to access.')
        
        function = self.namespace['functions'][method]
        
        # check whether all obligatory arguments are given
        ungiven_obligatory_args = list(set(function['args']['obligatory']) - \
            set(request_items.keys()))
        if ungiven_obligatory_args:
            raise RequestException(u'Obligatory argument(s) missing: %s' % \
                ", ".join(ungiven_obligatory_args))
        
        # check whether there are more arguments than needed
        if not function['args']['kwargs_allowed']:
            unsued_arguments = list(set(request_items.keys()) - \
                set(function['args']['obligatory']))
            
            if unsued_arguments:
                raise RequestException(u'Unused arguments: %s' % \
                ", ".join(unsued_arguments))
        
        # check allowed HTTP methods
        if not function['methods']['function'](self.http_request.method):
            raise RequestException(u'Method not allowed: %s' % self.http_request.method)
        
        # decode incoming variables
        for key, value in request_items.iteritems():
            request_items[key] = input_formatter.parse(value)

        # check constraints
        for key, value in request_items.iteritems():
            try:
                request_items[key] = function['constraints']['function'](
                    local_namespace, key, value)
            except:
                raise RequestException(u'Constraint failed for argument: %s' % key)
        
        # make the call
        result = getattr(local_namespace, method)(**request_items)
        
        # if result is already a Response, return it
        if isinstance(result, Response):
            return result
        
        return Response(
            self.http_request,
            result=result,
            output_formatter=output_formatter,
            wrapper=wrapper,
            mimetype=mimetype,
        )