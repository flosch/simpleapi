# -*- coding: utf-8 -*-

import cPickle
import hashlib
import warnings

__all__ = ('__builtin_features__', 'NamespaceFeature', 'FeatureResponse')

try:
    from django.core.cache import cache
except ImportError, e:
    # FIXME: dirty hack
    if not 'DJANGO_SETTINGS_MODULE' in str(e):
        raise

class FeatureResponse(object): 
    def __init__(self, data):
        self.data = data

class NamespaceFeature(object):
    def __init__(self, route, namespace):
        self.route = route
        self.namespace = namespace
    
    def _setup(self):
        if hasattr(self, 'setup'):
            self.setup()
    
    def _request(self, fname, fargs, ffunc, session_cache, request):
        if hasattr(self, 'request'):
            return self.request(fname, fargs, ffunc, session_cache, request)
    
    def _response(self, fname, fargs, fresult, ffunc, session_cache, request):
        if hasattr(self, 'response'):
            return self.response(fname, fargs, fresult, ffunc, session_cache, request)

    def error(self, err_or_list):
        self.namespace.error(err_or_list)

class PickleFeature(NamespaceFeature):
    __name__ = "pickle"
    
    def setup(self):
        
        class PickleType(object):

            __mime__ = "application/octet-stream"

            def build(self, data, callback):
                return cPickle.dumps(data)
            
            def parse(self, data):
                return cPickle.loads(data.encode("utf-8"))
        
        self.route.__response_types__['pickle'] = PickleType()
        self.route.__request_types__['pickle'] = PickleType()
        
        if not hasattr(self.namespace, '__authentication__'):
            warnings.warn(u'WARNING: You should activate __authentication__ since enabling pickle is a risk when used in an untrusted environment!')

class CachingFeature(NamespaceFeature):
    __name__ = "caching"
    
    def _build_arg_signature(self, fargs):
        return hashlib.md5(cPickle.dumps(fargs)).hexdigest()
    
    def request(self, fname, fargs, ffunc, session_cache, request):
        cache_details = getattr(ffunc, 'caching', None)
        if not cache_details: return
        
        key = cache_details.get('key', 'simpleapi_%s_%s' % (fname, self._build_arg_signature(fargs)))
        timeout = cache_details.get('timeout', 60*60)
        
        if callable(key):
            key = key(request)
        
        session_cache['cache_key'] = key
        session_cache['cache_timeout'] = timeout
        
        if cache.get(key):
            buf = cache.get(key)
            if buf is not None:
                return FeatureResponse(cPickle.loads(buf))
        else:
            session_cache['want_cached'] = True
    
    def response(self, fname, fargs, fresult, ffunc, session_cache, request):
        if session_cache.get('want_cached') is True:
            cache.set(session_cache['cache_key'], cPickle.dumps(fresult), session_cache['cache_timeout'])

__builtin_features__ = {
    'pickle': PickleFeature,
    'caching': CachingFeature,
}