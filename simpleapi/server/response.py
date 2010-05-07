# -*- coding: utf-8 -*-

import types

try:
    from django.http import HttpResponse as DjangoHttpResponse
    has_django = True
except ImportError:
    has_django = False

try:
    from flask import Response as FlaskResponse
    has_flask = True
except ImportError:
    has_flask = False

from simpleapi.message import formatters, wrappers
from preformat import Preformatter

__all__ = ('Response', 'ResponseException')

class ResponseException(object): pass
class Response(object):

    def __init__(self, sapi_request, namespace=None, output_formatter=None,
                 wrapper=None, errors=None, result=None, mimetype=None,
                 callback=None, session=None, function=None):
        assert isinstance(errors, (basestring, list)) or errors is None

        self.sapi_request = sapi_request
        self.namespace = namespace
        self.errors = errors
        self.result = self._preformat(result)
        self.mimetype = mimetype
        self.callback = None
        self.function = function

        self.output_formatter = output_formatter or formatters['json']
        self.wrapper = wrapper or wrappers['default']
        self.mimetype = mimetype or self.output_formatter.__mime__

        self.session = session

    def add_error(self, errmsg):
        if self.errors is None:
            self.errors = [errmsg, ]
        else:
            if isinstance(errors, list):
                self.errors.append(errmsg)
            elif isinstance(self.errors, basestring):
                self.errors = [self.errors, errmsg]

    def _preformat(self, value):
        preformatter = Preformatter()
        return preformatter.run(value)

    def build(self, skip_features=False):
        # call feature: handle_response
        if self.namespace and not skip_features:
            for feature in self.namespace['features']:
                feature._handle_response(self)

        # pass result to custom format function
        if self.function:
            self.result = self.function['format'](self.result)

        if isinstance(self.output_formatter, type):
            self.output_formatter = self.output_formatter(
                sapi_request=self.sapi_request,
                callback=self.callback
            )

        if isinstance(self.wrapper, type):
            self.wrapper = self.wrapper(
                errors=self.errors,
                result=self.result
            )

        wrapper_result = self.wrapper.build()
        formatter_result = self.output_formatter.build(wrapper_result)
        
        if self.sapi_request.is_flask():
            return FlaskResponse(
                response=formatter_result,
                mimetype=self.mimetype
            )
        elif self.sapi_request.is_django():
            return DjangoHttpResponse(
                formatter_result,
                mimetype=self.mimetype
            )