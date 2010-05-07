# -*- coding: utf-8 -*-

import copy
import inspect
import re

from sapirequest import SAPIRequest
from request import Request, RequestException
from response import Response, ResponseException
from namespace import NamespaceException
from feature import __features__, Feature, FeatureException
from simpleapi.message import formatters, wrappers
from utils import glob_list

__all__ = ('Route', )

class RouteException(Exception): pass
class Route(object):

    def __init__(self, *namespaces, **kwargs):
        """Takes at least one namespace. 
        """
        self.nmap = {}
        self.restful = kwargs.get('restful', False)
        self.framework = kwargs.get('framework', 'django')
        assert self.framework in ['flask', 'django']
        
        # for Flask support:
        self.__name__ = 'Route'

        for namespace in namespaces:
            self.add_namespace(namespace)

    def _redefine_default_namespace(self):
        # - recalculate default namespace version -
        # if map has no default version, determine namespace with the
        # highest version
        if self.nmap.has_key('default'):
            del self.nmap['default']
        self.nmap['default'] = self.nmap[max(self.nmap.keys())]

    def remove_namespace(self, version):
        if self.nmap.has_key(version):
            del self.nmap[version]
            self._redefine_default_namespace()
            return True
        else:
            return False

    def add_namespace(self, namespace):
        version = getattr(namespace, '__version__', 1)
        assert isinstance(version, int), u'version must be either an integer or not set'

        # make sure no version is assigned twice
        assert not self.nmap.has_key(version), u'version is assigned twice'

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
                        def check(namespace, key, value):
                            constraint = constraints.get(key)
                            if not constraint:
                                return value
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

                    constraint_function = check_constraint(constraints)
                elif callable(constraints):
                    constraint_function = constraints
            else:
                constraints = None
                constraint_function = lambda namespace, key, value: value

            # determine allowed methods
            if hasattr(function_method, 'methods'):
                allowed_methods = function_method.methods
                assert isinstance(allowed_methods, (list, tuple))
                method_function = lambda method: method in allowed_methods
            else:
                allowed_methods = None
                method_function = lambda method: True

            # determine format
            format = getattr(function_method, 'format', lambda val: val)

            functions[function_name] = {
                'method': function_method,
                'name': function_name,
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
                'format': format,
                'methods': {
                    'function': method_function,
                    'allowed_methods': allowed_methods,
                }
            }

        # configure authentication
        if hasattr(namespace, '__authentication__'):
            authentication = namespace.__authentication__
            if isinstance(authentication, basestring):
                authentication = lambda namespace, access_key: \
                    namespace.__authentication__ == access_key
        else:
            # grant allow everyone access
            authentication = lambda namespace, access_key: True

        # configure ip address based access rights
        if hasattr(namespace, '__ip_restriction__'):
            ip_restriction = namespace.__ip_restriction__
            assert isinstance(ip_restriction, list) or callable(ip_restriction)

            if isinstance(ip_restriction, list):
                # make the ip address list wildcard searchable
                namespace.__ip_restriction__ = glob_list(namespace.__ip_restriction__)

                # restrict access to the given ip address list
                ip_restriction = lambda namespace, ip: ip in namespace.__ip_restriction__
        else:
            # accept every ip address
            ip_restriction = lambda namespace, ip: True

        # configure input formatters
        input_formatters = formatters.copy()
        allowed_formatters = getattr(namespace, '__input__', 
            formatters.get_defaults())
        input_formatters = filter(lambda i: i[0] in allowed_formatters,
            input_formatters.items())
        input_formatters = dict(input_formatters)

        # configure output formatters
        output_formatters = formatters.copy()
        allowed_formatters = getattr(namespace, '__output__',
            formatters.get_defaults())
        output_formatters = filter(lambda i: i[0] in allowed_formatters,
            output_formatters.items())
        output_formatters = dict(output_formatters)

        # configure wrappers
        useable_wrappers = wrappers.copy()
        if hasattr(namespace, '__wrapper__'):
            allowed_wrapper = namespace.__wrapper__
            useable_wrappers = filter(lambda i: i[0] in allowed_wrapper,
                useable_wrappers.items())
            useable_wrappers = dict(useable_wrappers)

        self.nmap[version] = {
            'class': namespace,
            'functions': functions,
            'ip_restriction': ip_restriction,
            'authentication': authentication,
            'input_formatters': input_formatters,
            'output_formatters': output_formatters,
            'wrappers': useable_wrappers,
        }

        # set up all features
        features = []
        if hasattr(namespace, '__features__'):
            raw_features = namespace.__features__
            for feature in raw_features:
                assert isinstance(feature, basestring) or issubclass(feature, Feature)
                if isinstance(feature, basestring):
                    assert feature in __features__.keys(), \
                        u'%s is not a built-in feature' % feature
                    
                    features.append(__features__[feature](self.nmap[version]))
                elif issubclass(feature, Feature):
                    features.append(feature(self.nmap[version]))

        self.nmap[version]['features'] = features
        self._redefine_default_namespace()

        return version

    def __call__(self, http_request=None, **urlparameters):
        sapi_request = SAPIRequest(self, http_request)

        request_items = dict(sapi_request.REQUEST.items())
        request_items.update(urlparameters)
        
        version = request_items.pop('_version', 'default')
        callback = request_items.pop('_callback', None)
        output_formatter = request_items.pop('_output', None)

        # let's activate JSONP automatically if _callback is given
        if callback and not output_formatter:
            output_formatter = 'jsonp'
        elif not output_formatter:
            output_formatter = 'json'

        input_formatter = request_items.pop('_input', 'value')
        wrapper = request_items.pop('_wrapper', 'default')
        mimetype = request_items.pop('_mimetype', None)

        input_formatter_instance = None
        output_formatter_instance = None
        wrapper_instance = None

        try:
            try:
                version = int(version)
            except (ValueError, TypeError):
                pass
            if not self.nmap.has_key(version):
                # continue with wrong version to get the formatters/wrappers
                # raise the error later!
                namespace = self.nmap['default']
            else:
                namespace = self.nmap[version]

            # check input formatter
            if input_formatter not in namespace['input_formatters']:
                raise RequestException(u'Input formatter not allowed or ' \
                                        'unknown: %s' % input_formatter)

            # get input formatter
            input_formatter_instancec = namespace['input_formatters'][input_formatter](sapi_request, callback)

            # check output formatter
            if output_formatter not in namespace['output_formatters']:
                raise RequestException(u'Output formatter not allowed or ' \
                                        'unknown: %s' % output_formatter)

            # get output formatter
            output_formatter_instance = namespace['output_formatters'][output_formatter](sapi_request, callback)

            # check wrapper
            if wrapper not in namespace['wrappers']:
                raise RequestException(u'Wrapper unknown or not allowed: %s' % \
                    wrapper)

            # get wrapper
            wrapper_instance = namespace['wrappers'][wrapper]

            # check whether version exists or not
            if not self.nmap.has_key(version):
                raise RouteException(u'Version %s not found (possible: %s)' % \
                    (version, ", ".join(map(lambda i: str(i), self.nmap.keys()))))

            request = Request(
                sapi_request=sapi_request,
                namespace=namespace,
                input_formatter=input_formatter_instancec,
                output_formatter=output_formatter_instance,
                wrapper=wrapper_instance,
                callback=callback,
                mimetype=mimetype,
                restful=self.restful
            )
            response = request.run(request_items)
            http_response = response.build()
        except Exception, e:
            if isinstance(e, (NamespaceException, RequestException,
               ResponseException, RouteException, FeatureException)):
                err_msg = unicode(e)
            else:
                err_msg = u'An internal error occurred during your request.'
                trace = inspect.trace()
                msgs = []
                msgs.append('')
                msgs.append(u"******* Exception raised *******")
                msgs.append(u'Exception type: %s' % type(e))
                msgs.append(u'Exception msg: %s' % e)
                msgs.append('')
                msgs.append(u'------- Traceback follows -------')
                for idx, item in enumerate(trace):
                    msgs.append(u"(%s)\t%s:%s (%s)" % (idx+1, item[3], item[2], item[1]))
                    if item[4]:
                        for line in item[4]:
                            msgs.append(u"\t\t%s" % line.strip())
                    msgs.append('') # blank line
                msgs.append('     -- End of traceback --     ')
                msgs.append('')

                print "\n".join(msgs) # TODO: send it to the admins by email!

            response = Response(
                sapi_request,
                errors=err_msg,
                output_formatter=output_formatter_instance,
                wrapper=wrapper_instance,
                mimetype=mimetype
            )
            http_response = response.build(skip_features=True)

        return http_response