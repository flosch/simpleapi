# -*- coding: utf-8 -*-

from django.http import HttpResponse

from simpleapi.message import formatters, wrappers

__all__ = ('Response', 'ResponseException')

class ResponseException(object): pass
class Response(object):

    def __init__(self, http_request, namespace=None, output_formatter=None,
                 wrapper=None, errors=None, result=None, mimetype=None,
                 callback=None, session=None):
        self.http_request = http_request
        self.namespace = namespace
        self.errors = errors
        self.result = result
        self.mimetype = mimetype
        self.callback = None

        self.output_formatter = output_formatter or formatters['json']
        self.wrapper = wrapper or wrappers['default']
        self.mimetype = mimetype or self.output_formatter.__mime__

        self.session = session

    def build(self, skip_features=False):
        # call feature: handle_response
        if self.namespace and not skip_features:
            for feature in self.namespace['features']:
                feature._handle_response(self)

        if isinstance(self.output_formatter, type):
            self.output_formatter = self.output_formatter(
                http_request=self.http_request,
                callback=self.callback
            )

        if isinstance(self.wrapper, type):
            self.wrapper = self.wrapper(
                errors=self.errors,
                result=self.result
            )

        wrapper_result = self.wrapper.build()
        formatter_result = self.output_formatter.build(wrapper_result)

        return HttpResponse(
            formatter_result,
            mimetype=self.mimetype
        )