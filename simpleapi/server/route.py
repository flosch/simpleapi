# -*- coding: utf-8 -*-

import copy
import inspect
import pprint
import re
import sys
import os
import pdb
import cProfile
import pstats
import urlparse
import cgi
from wsgiref.simple_server import make_server
from wsgiref.handlers import SimpleHandler

SIMPLEAPI_DEBUG = bool(int(os.environ.get('SIMPLEAPI_DEBUG', 0)))
SIMPLEAPI_DEBUG_FILENAME = os.environ.get('SIMPLEAPI_DEBUG_FILENAME',
    'simpleapi.profile')
SIMPLEAPI_DEBUG_LEVEL = os.environ.get('SIMPLEAPI_DEBUG_LEVEL', 'all')
assert SIMPLEAPI_DEBUG_LEVEL in ['all', 'call'], \
    u'SIMPLEAPI_DEBUG_LEVEL must be one of these: all, call'

TRIGGERED_METHODS = ['get', 'post', 'put', 'delete']
FRAMEWORKS = ['flask', 'django', 'appengine', 'dummy', 'standalone', 'wsgi']
MAX_CONTENT_LENGTH = 1024 * 1024 * 16 # 16 megabytes

try:
    from google.appengine.ext.webapp import RequestHandler as AE_RequestHandler
    has_appengine = True
except ImportError:
    has_appengine = False

from sapirequest import SAPIRequest
from request import Request, RequestException
from response import Response, ResponseException
from namespace import NamespaceException
from feature import __features__, Feature, FeatureException
from simpleapi.message import formatters, wrappers
from utils import glob_list
import logging

__all__ = ('Route', )

class Route(object):

    def __new__(cls, *args, **kwargs):
        if kwargs.get('framework') == 'appengine':
            assert has_appengine
            class AppEngineRouter(AE_RequestHandler):
                def __getattribute__(self, name):
                    if name in TRIGGERED_METHODS:
                        self.request.method = name
                        return self
                    else:
                        return AE_RequestHandler.__getattribute__(self, name)
                                
                def __call__(self):
                    result = self.router(self.request)
                    self.response.out.write(result['result'])
            
            AppEngineRouter.router = Router(*args, **kwargs)
            return AppEngineRouter
        elif kwargs.get('framework') == 'flask':
            obj = Router(*args, **kwargs)
            obj.__name__ = 'Route'
            return obj
        elif kwargs.get('framework') == 'wsgi':
            router = Router(*args, **kwargs)
            class WSGIHandler(object):
                def __call__(self, *args, **kwargs):
                    return self.router.handle_request(*args, **kwargs)
            handler = WSGIHandler()
            handler.router = router
            return handler
        else:
            return Router(*args, **kwargs)

class StandaloneRequest(object): pass
class RouterException(Exception): pass
class Router(object):

    def __init__(self, *namespaces, **kwargs):
        """Takes at least one namespace. 
        """
        self.nmap = {}
        self.debug = kwargs.get('debug', False)
        self.restful = kwargs.get('restful', False)
        self.framework = kwargs.get('framework', 'django')
        self.path = re.compile(kwargs.get('path', r'^/'))
        
        # make shortcut 
        self._caller = self.__call__
        
        assert self.framework in FRAMEWORKS
        assert (self.debug ^ SIMPLEAPI_DEBUG) or \
            not (self.debug and SIMPLEAPI_DEBUG), \
            u'You can either activate Route-debug or simpleapi-debug, not both.'

        if self.debug or SIMPLEAPI_DEBUG:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.WARNING)
        
        if SIMPLEAPI_DEBUG and SIMPLEAPI_DEBUG_LEVEL == 'all':
            self.profile_start()

        for namespace in namespaces:
            self.add_namespace(namespace)

    def handle_request(self, environ, start_response):
        if not self.path.match(environ.get('PATH_INFO')): 
            status = '404 Not found'
            start_response(status, [])
            return ["Entry point not found"]
        else:
            content_type = environ.get('CONTENT_TYPE')
            try:
                content_length = int(environ['CONTENT_LENGTH'])
            except (KeyError, ValueError):
                content_length = 0

            # make sure we ignore too large requests for security and stability
            # reasons
            if content_length > MAX_CONTENT_LENGTH:
                status = '413 Request entity too large'
                start_response(status, [])
                return ["Request entity too large"]

            request_method = environ.get('REQUEST_METHOD', '').lower()

            # make sure we only support methods we care
            if not request_method in TRIGGERED_METHODS:
                status = '501 Not Implemented'
                start_response(status, [])
                return ["Not Implemented"]

            query_get = urlparse.parse_qs(environ.get('QUERY_STRING'))
            for key, value in query_get.iteritems():
                query_get[key] = value[0] # respect the first value only

            query_post = {}
            if content_type in ['application/x-www-form-urlencoded', 
                'application/x-url-encoded']:
                post_env = environ.copy()
                post_env['QUERY_STRING'] = ''
                fs = cgi.FieldStorage(
                    fp=environ['wsgi.input'],
                    environ=post_env,
                    keep_blank_values=True
                )
                query_post = {}
                for key in fs:
                    query_post[key] = fs.getvalue(key)
            elif content_type == 'multipart/form-data':
                # XXX TODO
                raise NotImplementedError, u'Currently not supported.' 
            
            # GET + POST 
            query_data = query_get
            query_data.update(query_post)

            # Make request
            request = StandaloneRequest()
            request.method = request_method
            request.data = query_data
            request.remote_addr = environ.get('REMOTE_ADDR', '')

            # Make call
            result = self._caller(request)

            status = '200 OK'
            headers = [('Content-type', result['mimetype'])]
            start_response(status, headers)
            return [result['result'],]

    def serve(self, host='', port=5050):
        httpd = make_server(host, port, self.handle_request)
        logging.info(u"Started serving on port %d..." % port)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            logging.info(u"Server stopped.")

    def profile_start(self):
        self.profile = cProfile.Profile()
        self.profile.enable()
    
    def profile_stop(self):
        self.profile.disable()
        self.profile.dump_stats(SIMPLEAPI_DEBUG_FILENAME)

    def profile_stats(self):
        logging.debug(u"Loading stats...")
        stats = pstats.Stats(SIMPLEAPI_DEBUG_FILENAME)
        stats.strip_dirs().sort_stats('time', 'calls') \
            .print_stats()

    def __del__(self):
        if SIMPLEAPI_DEBUG and SIMPLEAPI_DEBUG_LEVEL == 'all':
            self.profile_stop()
            self.profile_stats()

    def is_standalone(self):
        return self.framework in ['standalone', 'wsgi']

    def is_dummy(self):
        return self.framework == 'dummy'

    def is_appengine(self):
        return self.framework == 'appengine'

    def is_flask(self):
        return self.framework == 'flask'

    def is_django(self):
        return self.framework == 'django'

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
        assert isinstance(version, int), \
            u'version must be either an integer or not set'

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
                if hasattr(namespace, authentication):
                    authentication = getattr(namespace, authentication)
                else:
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
                namespace.__ip_restriction__ = \
                    glob_list(namespace.__ip_restriction__)

                # restrict access to the given ip address list
                ip_restriction = lambda namespace, ip: ip in \
                    namespace.__ip_restriction__
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
                assert isinstance(feature, basestring) or \
                    issubclass(feature, Feature)

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

        if SIMPLEAPI_DEBUG and SIMPLEAPI_DEBUG_LEVEL == 'call':
            logging.info(pprint.pformat(request_items))
            self.profile_start()

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
                raise RouterException(u'Version %s not found (possible: %s)' % \
                    (version, ", ".join(map(lambda i: str(i), self.nmap.keys()))))

            request = Request(
                sapi_request=sapi_request,
                namespace=namespace,
                input_formatter=input_formatter_instancec,
                output_formatter=output_formatter_instance,
                wrapper=wrapper_instance,
                callback=callback,
                mimetype=mimetype,
                restful=self.restful,
                debug=self.debug
            )
            response = request.run(request_items)
            http_response = response.build()
        except Exception, e:
            if isinstance(e, (NamespaceException, RequestException,
               ResponseException, RouterException, FeatureException)):
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
                    msgs.append(u"(%s)\t%s:%s (%s)" % 
                        (idx+1, item[3], item[2], item[1]))
                    if item[4]:
                        for line in item[4]:
                            msgs.append(u"\t\t%s" % line.strip())
                    msgs.append('') # blank line
                msgs.append('     -- End of traceback --     ')
                msgs.append('')
                logging.error("\n".join(msgs))

                if self.debug:
                    e, m, tb = sys.exc_info()
                    pdb.post_mortem(tb)

            response = Response(
                sapi_request,
                errors=err_msg,
                output_formatter=output_formatter_instance,
                wrapper=wrapper_instance,
                mimetype=mimetype
            )
            http_response = response.build(skip_features=True)

        if SIMPLEAPI_DEBUG and SIMPLEAPI_DEBUG_LEVEL == 'call':
            self.profile_stop()
            self.profile_stats()

        return http_response