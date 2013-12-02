# -*- coding: utf-8 -*-

import tempfile
import pprint
try:
    import cProfile
    import pstats
    has_debug = True
except ImportError:
    has_debug = False

from response import Response
from feature import FeatureContentResponse
from simpleapi.message import formatters
from simpleapi.message.common import SAException

try:
    from django.core.exceptions import ObjectDoesNotExist as django_notexist
    has_django = True
except:
    has_django = False

try:
    from mongoengine.queryset import DoesNotExist as mongoengine_notexist
    has_mongoengine = True
except ImportError:
    has_mongoengine = False

__all__ = ('Request', 'RequestException')

class RequestException(SAException): pass
class Request(object):

    def __init__(self, sapi_request, namespace, input_formatter,
                 output_formatter, wrapper, callback, mimetype, restful,
                 debug, route, ignore_unused_args):
        self.sapi_request = sapi_request
        self.namespace = namespace
        self.input_formatter = input_formatter
        self.output_formatter = output_formatter
        self.wrapper = wrapper
        self.callback = callback
        self.mimetype = mimetype
        self.restful = restful
        self.debug = debug
        self.route = route
        self.ignore_unused_args = ignore_unused_args
        self.session = sapi_request.session

    def process_request(self, request_items):
        # set all required simpleapi arguments
        access_key = request_items.pop('_access_key', None)
        method = request_items.pop('_call', None)

        if self.restful:
            method = self.sapi_request.method.lower()

        data = request_items.pop('_data', None)

        # update session
        self.session.request = self.sapi_request
        self.session.mimetype = self.mimetype
        self.session.callback = self.callback
        self.session.access_key = access_key

        # make all uploaded files available
        if self.route.is_django():
            self.session.files = self.sapi_request.FILES

        # instantiate namespace
        local_namespace = self.namespace['class'](self)
        self.session._internal.namespace = {
            'nmap': self.namespace,
            'instance': local_namespace
        }

        # check the method
        if not method:
            raise RequestException(u'Method must be provided.')

        # check whether method exists
        if not self.namespace['functions'].has_key(method):
            raise RequestException(u'Method %s does not exist.' % method)

        # check authentication
        if not self.namespace['authentication'](local_namespace, access_key):
            raise RequestException(u'Authentication failed.')

        # check ip address
        if not self.namespace['ip_restriction'](local_namespace, \
                                                self.sapi_request.remote_addr):
            raise RequestException(u'You are not allowed to access.')

        function = self.namespace['functions'][method]
        self.session.function = function

        # check allowed HTTP methods
        if not function['methods']['function'](self.sapi_request.method, function['methods']['allowed_methods']):
            raise RequestException(u'Method not allowed: %s' % self.sapi_request.method)

        # if data is set, make sure input formatter is not ValueFormatter
        if data:
            if isinstance(self.input_formatter, formatters['value']):
                raise RequestException(u'If you\'re using _data please make ' \
                                        'sure you set _input and _input is not ' \
                                        '\'value\'.')
            try:
                request_items = self.input_formatter.kwargs(data, 'parse')
            except ValueError, _:
                raise RequestException(u'Data couldn\'t be decoded. ' \
                                        'Please check _input and your _data')
            else:
                if not isinstance(request_items, dict):
                    raise RequestException(u'_data must be an array/dictionary')

        # check whether all obligatory arguments are given
        ungiven_obligatory_args = list(set(function['args']['obligatory']) - \
            set(request_items.keys()))
        if ungiven_obligatory_args:
            raise RequestException(u'Obligatory argument(s) missing: %s' % \
                ", ".join(ungiven_obligatory_args))

        # check whether there are more arguments than needed
        if not function['args']['kwargs_allowed']:
            unused_arguments = list(set(request_items.keys()) - \
                set(function['args']['all']))

            if unused_arguments:
                if not self.ignore_unused_args:
                    raise RequestException(u'Unused arguments: %s' % \
                    ", ".join(unused_arguments))
                else:
                    for key in unused_arguments:
                        del request_items[key]

        # decode incoming variables (only if _data is not set!)
        if not data:
            new_request_items = {}
            for key, value in request_items.iteritems():
                try:
                    new_request_items[str(key)] = self.input_formatter.kwargs(value, 'parse')
                except ValueError, _:
                    raise
                    raise RequestException(u'Value for %s couldn\'t be decoded.' % \
                        key)
            request_items = new_request_items
        else:
            # make sure all keys are strings, not unicodes (for compatibility 
            # issues: Python < 2.6.5)
            new_request_items = {}
            for key, value in request_items.iteritems():
                new_request_items[str(key)] = value
            request_items = new_request_items

        # check constraints
        for key, value in request_items.iteritems():
            try:
                request_items[key] = function['constraints']['function'](
                    local_namespace, key, value)
            except (ValueError,):
                raise RequestException(u'Constraint failed for argument: %s' % key)

        # we're done working on arguments, pass it to the session
        self.session.arguments = request_items

        # call feature: handle_request
        try:
            for feature in self.namespace['features']:
                feature._handle_request(self)
        except FeatureContentResponse, e:
            result = e
        else:
            # call before_request
            if hasattr(local_namespace, 'before_request'):
                getattr(local_namespace, 'before_request')(self, self.session)
            
            # make the call
            try:
                if self.debug:
                    _, fname = tempfile.mkstemp()
                    self.route.logger.debug(u"Profiling call '%s': %s" % \
                        (method, fname))

                    self.route.logger.debug(u"Calling parameters: %s" % \
                        pprint.pformat(request_items))

                    profile = cProfile.Profile()
                    result = profile.runcall(getattr(local_namespace, method),
                        **request_items)
                    profile.dump_stats(fname)
                    
                    self.route.logger.debug(u"Loading stats...")
                    stats = pstats.Stats(fname)
                    stats.strip_dirs().sort_stats('time', 'calls') \
                        .print_stats(25)
                else:
                    result = getattr(local_namespace, method)(**request_items)
            except Exception, e:
                if has_django and isinstance(e, django_notexist):
                    raise RequestException(e)
                elif has_mongoengine and isinstance(e, mongoengine_notexist):
                    raise RequestException(e)
                else:
                    raise

        # if result is not a Response, create one
        if not isinstance(result, Response):
            response = Response(
                sapi_request=self.sapi_request,
                namespace=self.namespace,
                result=result,
                output_formatter=self.output_formatter,
                wrapper=self.wrapper,
                mimetype=self.mimetype,
                function=function
            )
        else:
            response = result

        return response