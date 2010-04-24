# -*- coding: utf-8 -*-

import cPickle
import hashlib
import warnings

from formatter import Formatter

try:
    from django.core.cache import cache
except ImportError, e:
    # FIXME: dirty hack? how can we prevent that the
    # Client library raises an error if django settings isn't present
    if not 'DJANGO_SETTINGS_MODULE' in str(e):
        raise

__all__ = ('__features__', 'FeatureContentResponse')

class FeatureContentResponse(Exception): pass
class Feature(object):
    
    def __init__(self, ns_config):
        self.ns_config = ns_config
        self.setup()

    def setup(self):
        pass
    
    def handle_request(self, request):
        pass
    
    def handle_response(self, response):
        pass

class PickleFeature(Feature):
    
    def setup(self):
        class PickleFormatter(Formatter):
            __mime__ = "application/octet-stream"
    
            def build(self, value):
                return cPickle.dumps(value)
    
            def parse(self, value):
                return cPickle.loads(value.encode("utf-8"))
        
        self.ns_config['input_formatters']['pickle'] = PickleFormatter
        self.ns_config['output_formatters']['pickle'] = PickleFormatter

class CachingFeature(Feature):
    
    def handle_request(self, request):
        caching_config = getattr(request.session.function['method'], 'caching', None)
        if caching_config:
            arg_signature = hashlib.md5(cPickle.dumps(request.session.arguments)).hexdigest()
            timeout = 60*60
            prefix = None
            
            if isinstance(caching_config, dict):
                timeout = caching_config.get('timeout', timeout)
                prefix = caching_config.get('key', None)
                if callable(prefix):
                    prefix = prefix(request)
            
            key = '%s_%s' % (
                prefix or ('simpleapi_%s' % request.session.function['name']),
                arg_signature,
            )
            
            content = cache.get(key)
            
            if content:
                raise FeatureContentResponse(cPickle.loads(content))
            else:
                request.session.cache_timeout = timeout
                request.session.cache_key = key
                request.session.want_cached = True
    
    def handle_response(self, response):
        # only cache if function returns no errors!
        if hasattr(response.session, 'want_cached') and not response.errors:
            cache.set(
                response.session.cache_key,
                cPickle.dumps(response.result),
                response.session.cache_timeout
            )

__features__ = {
    'pickle': PickleFeature,
    'caching': CachingFeature
}