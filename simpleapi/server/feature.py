# -*- coding: utf-8 -*-

import cPickle
import hashlib
import warnings

from simpleapi.message import formatters, Formatter

try:
    from django.core.cache import cache
    has_django = True
except:
    has_django = False

__all__ = ('__features__', 'Feature', 'FeatureException', 'FeatureContentResponse')

class FeatureException(Exception): pass
class FeatureContentResponse(FeatureException): pass
class Feature(object):

    def __init__(self, ns_config):
        self.ns_config = ns_config
        self.setup()

    def error(self, errmsg):
        raise FeatureException(errmsg)

    def get_config_scope(self, request):
        assert self.has_config()

        conf_name, conf_type = self._get_config_values()

        if hasattr(self, '__config__'):
            function_location = hasattr(request.session.function['method'], conf_name)

            if function_location:
                return u'local:%s' % request.session.function['name']
            else:
                return 'global'
        elif hasattr(self, '__function_config__'):
            return u'local:%s' % request.session.function['name']
        elif hasattr(self, '__class_config__'):
            return 'global'

    def has_config(self):
        return hasattr(self, '__config__') or hasattr(self, '__class_config__') or \
               hasattr(self, '__function_config__')

    def get_config(self, request):
        assert self.has_config()

        conf_name, conf_type = self._get_config_values()

        if hasattr(self, '__config__'):
            class_value = getattr(request.session.namespace['nmap']['class'], conf_name, None)
            function_value = getattr(request.session.function['method'], conf_name, None)

            # prefer function based conf. over class based conf.
            if function_value is not None:
                return function_value
            else:
                return class_value
        elif hasattr(self, '__function_config__'):
            return getattr(request.session.function['method'], conf_name, None)
        elif hasattr(self, '__class_config__'):
            return getattr(request.session.namespace['nmap']['class'], conf_name, None)

    def _get_config_values(self):
        if hasattr(self, '__config__'):
            conf_name, conf_type = self.__config__
        elif hasattr(self, '__function_config__'):
            conf_name, conf_type = self.__function_config__
        elif hasattr(self, '__class_config__'):
            conf_name, conf_type = self.__class_config__

        return conf_name, conf_type

    def is_triggered(self, request):
        if self.has_config():
            conf_name, conf_type = self._get_config_values()
            conf_value = self.get_config(request)
            if isinstance(conf_value, conf_type):
                return True
            else:
                return False
        else:
            return True

    def _handle_request(self, request):
        if self.is_triggered(request):
            self.handle_request(request)

    def _handle_response(self, response):
        if self.is_triggered(response):
            self.handle_response(response)

    def setup(self): pass
    def handle_request(self, request): pass
    def handle_response(self, response): pass

class CachingFeature(Feature):

    __config__ = ('caching', (dict, bool))

    def setup(self):
        assert has_django, 'Works currently with django only'

    def handle_request(self, request):
        caching_config = self.get_config(request)

        if caching_config:
            arg_signature = hashlib.md5(cPickle.dumps(
                request.session.arguments)).hexdigest()

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

class ThrottlingFeature(Feature):

    __config__ = ('throttling', dict)

    def setup(self):
        assert has_django, 'Works currently with django only'

    def handle_request(self, request):
        throttling_config = self.get_config(request)
        scope = self.get_config_scope(request)

        rps = throttling_config.get('rps', 0)
        rpm = throttling_config.get('rpm', 0)
        rph = throttling_config.get('rph', 0)

        assert rps >= 0
        assert rpm >= 0
        assert rph >= 0

        remote_addr = request.session.request.remote_addr
        key = 'simpleapi_throttling_%s:%s' % (scope, remote_addr)
        rps_key = '%s_rps' % key
        rpm_key = '%s_rpm' % key
        rph_key = '%s_rph' % key

        # increment + check limits
        if rps > 0:
            no = cache.get(rps_key, 1)
            if no >= rps:
                self.error(u'Throttling active (exceeded %s #/sec.)' % no)
            else:
                try:
                    cache.incr(rps_key) # FIXME: using incr() eliminates the timeout!
                except ValueError:
                    cache.set(rps_key, 1, 1)

        if rpm > 0:
            no = cache.get(rpm_key, 1)
            if no >= rpm:
                self.error(u'Throttling active (exceeded %s #/min.)' % no)
            else:
                try:
                    cache.incr(rpm_key)
                except ValueError:
                    cache.set(rpm_key, 1, 60)

        if rph > 0:
            no = cache.get(rph_key, 1)
            if no >= rph:
                self.error(u'Throttling active (exceeded %s #/hour)' % no)
            else:
                try:
                    cache.incr(rph_key)
                except ValueError:
                    cache.set(rph_key, 1, 60*60)

__features__ = {
    'caching': CachingFeature,
    'throttling': ThrottlingFeature
}