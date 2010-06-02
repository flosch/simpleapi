# -*- coding: utf-8 -*-

try:
    from flask import request as flask_request
    has_flask = True
except ImportError:
    has_flask = False

class SAPIRequest(object):
    
    def __init__(self, route, request=None):
        self.route = route

        if not request:
            if route.is_flask():
                assert has_flask
                request = flask_request
            else:
                raise ValueError(u'HttpRequest-object is missing')

        self.request = request

    @property
    def GET(self):
        if self.route.is_flask():
            return self.request.args
        elif self.route.is_django():
            return self.request.GET

    @property
    def POST(self):
        if self.route.is_flask():
            return self.request.args
        elif self.route.is_django():
            return self.request.POST

    @property
    def REQUEST(self):
        if self.route.is_flask():
            return self.request.args
        elif self.route.is_django():
            return self.request.REQUEST

    @property
    def META(self):
        if self.is_flask():
            return self.request.environ
        elif self.is_django():
            return self.request.META

    @property
    def method(self):
        if self.is_flask():
            return self.request.method
        elif self.is_django():
            return self.request.method