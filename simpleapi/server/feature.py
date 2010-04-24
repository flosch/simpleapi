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

__all__ = ('__features__', )

class Feature(object):
    
    def __init__(self, ns_config):
        self.ns_config = ns_config
    
    def handle_request(self, request):
        pass
    
    def handle_response(self, response):
        pass

class PickleFeature(Feature):
    
    def __init__(self, *args, **kwargs):
        super(PickleFeature, self).__init__(*args, **kwargs)
        
        class PickleFormatter(Formatter):
            __mime__ = "application/octet-stream"
    
            def build(self, value):
                return cPickle.dumps(value)
    
            def parse(self, value):
                return cPickle.loads(value.encode("utf-8"))
        
        self.ns_config['input_formatters']['pickle'] = PickleFormatter
        self.ns_config['output_formatters']['pickle'] = PickleFormatter
    
    def handle_request(self, request):
        pass

class CachingFeature(Feature):
    
    pass

__features__ = {
    'pickle': PickleFeature,
    'caching': CachingFeature
}