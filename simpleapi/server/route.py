# -*- coding: utf-8 -*-

import inspect
import re

from request import Request, RequestException
from response import Response, ResponseException
from namespace import NamespaceException
from utils import glob_list

__all__ = ('Route', )

class RouteException(Exception): pass
class Route(object):
    
    def __init__(self, *namespaces):
        nmap = {}
        
        for namespace in namespaces:
            version = getattr(namespace, '__version__', 'default')
            assert isinstance(version, int) or version == 'default', \
                u'version must be either an integer or not set'
            
            # make sure no version is assigned twice
            assert not nmap.has_key(version), u'version is assigned twice'
            
            # determine public and published functions
            functions = filter(lambda item: '__' not in item[0] and 
                getattr(item[1], 'published', False) == True,
                inspect.getmembers(namespace))
            
            # determine arguments of each function
            functions = dict(functions)
            for function_name, function_method in functions.iteritems():
                # ArgSpec(args=['self', 'a', 'b'], varargs=None, keywords=None, defaults=None)
                raw_args = inspect.getargspec(function_method)
                
                # does the function allows kwargs?
                kwargs_allowed = raw_args[2] is not None
                
                # get all arguments
                all_args = raw_args[0][1:] # exclude `self´
                
                # build a dict of optional arguments
                if raw_args[3] is not None:
                    default_args = zip(
                        raw_args[0][-len(raw_args[3]):],
                        raw_args[3]
                    )
                    default_args = dict(default_args)
                else:
                    default_args = {}
                
                # build a list of obligatory arguments
                obligatory_args = list(set(all_args) - set(default_args.keys()))
                
                # determine constraints for function
                if hasattr(function_method, 'constraints'):
                    constraints = function_method.constraints
                    assert isinstance(constraints, dict) or callable(constraints)
                    
                    if isinstance(constraints, dict):
                        def check_constraint(constraints):
                            def check(key, value):
                                constraint = constraints.get(key)
                                if hasattr(constraint, 'match'):
                                    if constraint.match(value):
                                        return value
                                    else:
                                        raise ValueError(u'%s does not match constraint')
                                else:
                                    if isinstance(constraint, bool):
                                        return bool(int(value))
                                    else:
                                        return constraint(value)
                            return check
                        
                        constraint_function = check_constraint
                    elif callable(constraints):
                        constraint_function = constraints
                else:
                    constraints = None
                    constraint_function = lambda k, v: v
                
                # determine allowed methods
                if hasattr(function_method, 'methods'):
                    allowed_methods = function_method.methods
                    assert isinstance(allowed_methods, (list, tuple))
                    method_function = lambda method: method in allowed_methods
                else:
                    allowed_methods = None
                    method_function = lambda method: True
                
                functions[function_name] = {
                    'method': function_method,
                    'args': {
                        'raw': raw_args,
                        'all': all_args,
                        
                        'obligatory': obligatory_args,
                        'defaults': default_args,
                        
                        'kwargs_allowed': kwargs_allowed
                    },
                    'constraints': {
                        'function': constraint_function,
                        'raw': constraints,
                    },
                    'methods': {
                        'function': method_function,
                        'allowed_methods': allowed_methods,
                    }
                }
            
            # configure authentication
            # TODO
            authentication = None
            
            # configure ip address based access rights
            if hasattr(namespace, '__ip_restriction__'):
                ip_restriction = namespace.__ip_restriction__
                assert isinstance(ip_restriction, list) or callable(ip_restriction)
                
                if isinstance(ip_restriction, list):
                    # make the ip address list wildcard searchable
                    namespace.__ip_restriction__ = glob_list(namespace.__ip_restriction__)
                    
                    # restrict access to the given ip address list
                    ip_restriction = lambda ip: ip in namespace.__ip_restriction__
            else:
                # accept every ip address
                ip_restriction = lambda ip: True
            
            nmap[version] = {
                'class': namespace,
                'functions': functions,
                'ip_restriction': ip_restriction,
                'authentication': authentication,
            }
        
        # if map has no default version, determine namespace with the 
        # highest version 
        if not nmap.has_key('default'):
            nmap['default'] = nmap[max(nmap.keys())]
        
        self.nmap = nmap
    
    def __call__(self, http_request):
        version = http_request.REQUEST.get('_version', 'default')
        try:
            if not self.nmap.has_key(version):
                raise RouteException(u'Version %s not found (possible: %s)' % \
                    (version, ", ".join(self.nmap.keys())))
            
            namespace = self.nmap[version]
        
            request = Request(http_request, namespace)
            response = request.run()
        except (NamespaceException, RequestException, ResponseException,
                RouteException), e:
            response = Response(errors=unicode(e))
        except:
            raise # TODO handling
        
        http_response = response.build()
        
        return http_response