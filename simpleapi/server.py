# -*- coding: utf-8 -*-

try:
    import json
except ImportError:
    import simplejson as json
import inspect

from django.conf import settings
from django.http import HttpResponse

from features import *
from utils import glob_list

__all__ = ('Namespace', 'Route')

class NamespaceSession(object):
    
    def __init__(self, session_data):
        self.data = session_data
    
    def __getattr__(self, name):
        return self.data.get(name)

class NamespaceException(Exception): pass
class Namespace(object):
    
    def __init__(self, session_data):
        self.session = NamespaceSession(session_data)
    
    def error(self, err_or_list):
        raise ResponseException(err_or_list)

class JSONType(object):
    
    __mime__ = "application/json"
    
    def build(self, data, callback):
        return json.dumps(data)
    
    def parse(self, data):
        return json.loads(data)

class JSONPType(object):
    
    __mime__ = "application/javascript"
    
    def build(self, data, callback):
        return u'%s(%s)' % (callback or 'simpleapiCallback', json.dumps(data))

class XMLType(object):
    
    __mime__ = "text/xml"
    
    def build(self, data, callback):
        raise NotImplemented

class RouteException(Exception): pass
class ResponseException(RouteException): pass

class Route(object):
    
    __response_types__ = {
        'json': JSONType(),
        'jsonp': JSONPType(),
        'xml': XMLType()
    }
    
    __request_types__ = {
        'value': None,
        'json': JSONType()
    }
    
    def __init__(self, *namespaces):
        self.namespace_map = {}
        
        for namespace in namespaces:
            version = getattr(namespace, '__version__', 'default')
            
            if self.namespace_map.has_key(version):
                raise ValueError(u'Duplicate API version')
            
            functions = filter(lambda fn: '__' not in fn[0],
                dict(inspect.getmembers(namespace)).items())
            
            functions = filter(lambda fn: 
                getattr(fn[1], 'published', False) == True, functions)
            
            functions = map(lambda item: (item[0], {'fn': item[1], 'vars':
                inspect.getargspec(item[1])}), functions)
            
            functions = dict(functions)
            
            self.namespace_map[version] = {
                'class': namespace,
                'functions': functions
            }
            
            # make glob list from ip address ranges
            if hasattr(namespace, '__ip_restriction__'):
                self.namespace_map[version]['class'].__ip_restriction__ = \
                    glob_list(namespace.__ip_restriction__)
            
            # __features__      apply features
            if hasattr(namespace, '__features__'):
                self.namespace_map[version]['features'] = {}
                for feature in namespace.__features__:
                    if isinstance(feature, basestring):
                        if not __builtin_features__.has_key(feature):
                            raise ValueError(u'feature %s not found' % feature)
                        
                        feature = __builtin_features__[feature](
                            self, self.namespace_map[version]['class'])
                        assert hasattr(feature, '__name__')
                        
                        self.namespace_map[version]['features'][feature.__name__] = feature
                        feature._setup()
                    else:
                        raise NotImplemented
        
        # create default namespace (= latest version)
        self.namespace_map['default'] = self.namespace_map[max(self.namespace_map.keys())]
    
    def _build_response(self, data=None, response_type='json', errors=None,
                        success=None, callback=None, mimetype=None):
        result = {}
        
        if errors is not None:
            result['errors'] = isinstance(errors, list) and errors or [unicode(errors),]
        
        if success is None:
            success = errors is None
        result['success'] = success
        
        if data is not None:
            result['result'] = data
        
        resp_type_inst = self.__response_types__[response_type]
        
        return HttpResponse(
            resp_type_inst.build(result, callback),
            mimetype=mimetype or getattr(resp_type_inst, '__mime__', 'text/plain')
        )
    
    def _parse_request(self, rvars, request_type):
        for key, value in rvars.iteritems():
            rvars[key] = self.__request_types__[request_type].parse(value)
        return rvars
    
    def _get_function(self, fname, version):
        namespace_item = self.namespace_map[version]
        functions = namespace_item['functions']
        
        if fname not in functions.keys():
            raise ResponseException(u'Method (%s) not found' % fname)
        
        return functions[fname]
    
    def _handle_request(self, request, rvars, fname, fitem, namespace,
                        version):
        func = fitem['fn']
        
        # check methods
        if hasattr(func, 'methods'):
            assert isinstance(func.methods, tuple)
            if request.method not in func.methods:
                raise ResponseException(
                    u'HTTP-method not supported (supported: %s)' % \
                        ", ".join(func.methods))
        
        args = []
        kwargs = {}
        
        # var arguments
        if fitem['vars'][3] is not None:
            var_args = fitem['vars'][0][1:-len(fitem['vars'][3])]
        else:
            var_args = fitem['vars'][0][1:]
        
        for arg in var_args:
            try:
                args.append((arg, rvars.pop(arg)))
            except KeyError:
                raise ResponseException(u'Argument %s is missing' % arg)
        
        # optional arguments
        if fitem['vars'][3]:
            for arg in fitem['vars'][0][-len(fitem['vars'][3]):]:
                try:
                    kwargs[arg] = rvars.pop(arg)
                except KeyError:
                    pass

        # are there any vars left?
        # if true, they are only allowed when func takes **kwargs
        if len(rvars) > 0 and fitem['vars'][2] is None:
            raise ResponseException(u'Unused argument(s): %s' % \
                ", ".join(rvars.keys()))
        
        # update kwargs if func takes **kwargs
        if fitem['vars'][2] is not None:
            kwargs.update(rvars)
        
        # ensure constraints
        if hasattr(func, 'constraints'):
            assert isinstance(func.constraints, dict) or callable(func.constraints)
            
            if isinstance(func.constraints, dict):
                for var_name, var_type in func.constraints.iteritems():
                    if var_name not in fitem['vars'][0]:
                        message = u'%s not found in function argument list' % \
                            var_name
                        raise ValueError(message)
                
                    def convert(value, vtype):
                        if hasattr(vtype, 'match'):
                            if vtype.match(value) is None:
                                message = u'Argument %s must fulfil ' \
                                          u'constraint (regex)' % var_name
                                raise ResponseException(message)
                        else:
                            try:
                                if vtype == bool:
                                    return vtype(int(value))
                                else:
                                    return vtype(value)
                            except (ValueError, TypeError):
                                if hasattr(vtype, 'name'):
                                    vtype_name = vtype.name
                                else:
                                    vtype_name = repr(vtype)

                                message = u'Argument %s must contain: %s' % \
                                    (var_name, vtype_name)
                                raise ResponseException(message)
                    
                    new_args = []
                    for key, value in args:
                        if key == var_name:
                            new_args.append((key, convert(value, var_type)))
                        else:
                            new_args.append((key, value))
                    args = new_args
                    
                    if kwargs.has_key(var_name):
                        kwargs[var_name] = convert(value, var_type)
            elif callable(func):
                def convert_via_callable(key, value):
                    try:
                        return func.constraints(namespace, key, value)
                    except (ValueError, TypeError), e:
                        message = u'Argument %s must fulfil constraint' % key
                        raise ResponseException(message)
                
                # args
                for key, value in dict(args).iteritems():
                    new_args = []
                    for akey, avalue in args:
                        if akey == key:
                            new_args.append((akey, convert_via_callable(akey, avalue)))
                        else:
                            new_args.append((akey, avalue))
                
                    args = new_args
                
                # kwargs
                for key, value in kwargs.iteritems():
                    kwargs[key] = convert_via_callable(key, value)
        
        # trigger feature REQUEST
        features = self.namespace_map[version].get('features')
        if features:
            session_cache = {}
            for name, feature in features.iteritems():
                feature_result = feature._request(fname, (args, kwargs), func, session_cache, request)
                if isinstance(feature_result, FeatureResponse):
                    return feature_result.data
        
        try:
            args = map(lambda i: i[1], args)
            result = func(namespace, *args, **kwargs)
        except Exception, e:
            if not isinstance(e, ResponseException):
                trace = inspect.trace()
                msgs = []
                msgs.append('')
                msgs.append(u"******* Exception raised *******")
                msgs.append(u"Function call: %s" % fname)
                msgs.append(u"Variables: %s, %s" % (args, kwargs))
                msgs.append(u'Exception type: %s' % type(e))
                msgs.append(u'Exception msg: %s' % e)
                msgs.append('')
                msgs.append(u'------- Traceback follows -------')
                for idx, item in enumerate(trace):
                    msgs.append(u"(%s)\t%s:%s (%s)" % (idx+1, item[3], item[2], item[1]))
                    for line in item[4]:
                        msgs.append(u"\t\t%s" % line.strip())
                    msgs.append('') # blank line
                msgs.append('     -- End of traceback --     ')
                msgs.append('')
                print "\n".join(msgs) # TODO send it to the admins by email!
                raise ResponseException(u'An internal error occurred during your request.')
            else:
                raise
        
        # trigger feature RESPONSE
        if features:
            for name, feature in features.iteritems():
                feature_result = feature._response(fname, rvars, result, func, session_cache, request)
                if isinstance(feature_result, FeatureResponse):
                    return feature_result.data
        
        return result
    
    def __call__(self, request):
        rvars = dict(request.REQUEST.items())
        
        # _mimetype     get mimetype
        mimetype = rvars.pop('_mimetype', None)
        
        # _callback     get callback for jsonp
        callback = rvars.pop('_callback', '')
        
        # _version      check version
        version = rvars.pop('_version', 'default')
        
        if version <> 'default':
            try:
                version = int(version)
            except ValueError:
                return self._build_response(
                    errors=u'API-version must be an integer (available ' \
                           u'versions: %s)' % ", ".join(
                                map(lambda x: str(x), self.namespace_map.keys()))
                            )
        
        if not self.namespace_map.has_key(version):
            return self._build_response(
                errors=u'API-version not found (available versions: %s)' % \
                    ", ".join(map(lambda x: str(x), self.namespace_map.keys())))
        
        # determine default namespace-class
        namespace_class = self.namespace_map[version]['class']
        
        # instantiate connection-based namespace
        namespace = namespace_class({
            'request': request,
            'version' :version,
            'mimetype': mimetype,
            'callback': callback
        })
        
        # _access_key   check authentication
        access_key = rvars.pop('_access_key', None)
        if hasattr(namespace, '__authentication__'):
            if not access_key:
                return self._build_response(errors=u'Please provide an access key')
            
            if not namespace.__authentication__:
                raise ValueError(u'If you want use authentication, you must provide either a static key or a callable.')
            
            if isinstance(namespace.__authentication__, basestring):
                if access_key <> namespace.__authentication__:
                    return self._build_response(errors=u'Wrong access key')
            elif callable(namespace.__authentication__):
                if not namespace.__authentication__(access_key):
                    return self._build_response(errors=u'Wrong access key')
            else:
                raise ValueError(u'__authentication__ can be either a callable or a string, not %s' % type(namespace.__authentication__))
            
            namespace.session.data['access_key'] = access_key
        
        # __ip_restriction__        check ipaddress restriction
        if hasattr(namespace, '__ip_restriction__'):
            if callable(namespace.__ip_restriction__):
                if not namespace.__ip_restriction__(request.META.get('REMOTE_ADDR')):
                    return self._build_response(errors=u'permission denied')
            elif request.META.get('REMOTE_ADDR', 'n/a') not in namespace.__ip_restriction__:
                return self._build_response(errors=u'permission denied')
        
        # _output       get output formatter
        response_type = rvars.pop('_output', 'json')
        if callback:
            # if callback is set, automagically set response_type to jsonp
            response_type = 'jsonp'
        
        if response_type not in self.__response_types__.keys():
            return self._build_response(errors=u'Response type (%s) not found' % response_type)
        
        # _input        request type
        request_type = rvars.pop('_input', 'value')
        if request_type is not None and request_type not in self.__request_types__.keys():
            return self._build_response(errors=u'Request type (%s) not found' % request_type)
        
        # __outputs__       check against output
        if hasattr(namespace, '__outputs__'):
            if response_type not in namespace.__outputs__:
                return self._build_response(errors=u'Response type not allowed')
        
        # __inputs__        check against output
        if hasattr(namespace, '__inputs__'):
            if request_type not in namespace.__inputs__:
                return self._build_response(errors=u'Request type not allowed')
        
        # _call     get desired method name
        try:
            fname = rvars.pop('_call')
        except KeyError:
            return self._build_response(errors=u'_call not given')
        
        # all system parameters are removed, let's parse the request
        if request_type <> 'value':
            try:
                rvars = self._parse_request(rvars, request_type)
            except:
                return self._build_response(
                    errors=u'There was an error during decoding your inputs.' \
                           u'Please check whether you chose the correct' \
                           u'input-type and you\'ve coded the inputs appropriately!')
        
        try:
            fitem = self._get_function(fname, version)
            
            # check whether output configuration is set
            func = fitem['fn']
            
            if hasattr(func, 'outputs'):
                assert isinstance(func.outputs, list) or isinstance(func.outputs, tuple)
                if response_type not in func.outputs:
                    return self._build_response(
                        errors=u'Response type (%s) not allowed (allowed: %s)' % \
                            (response_type, ", ".join(func.outputs)))
            
            return self._build_response(
                self._handle_request(
                    request,
                    rvars,
                    fname,
                    fitem,
                    namespace,
                    version
                ),
                response_type=response_type,
                callback=callback,
                mimetype=mimetype
            )
        except ResponseException, e:
            return self._build_response(
                response_type=response_type,
                errors=e
            )