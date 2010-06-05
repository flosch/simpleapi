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
            elif route.is_appengine():
                request = route.request
            else:
                raise ValueError(u'HttpRequest-object is missing')

        self.request = request

    @property
    def GET(self):
        if self.route.is_flask():
            return self.request.args
        elif self.route.is_django():
            return self.request.GET
        elif self.route.is_appengine():
            return self.request.REQUEST
        elif self.route.is_dummy() or self.route.is_standalone():
            return self.request.data
        raise NotImplementedError

    @property
    def POST(self):
        if self.route.is_flask():
            return self.request.args
        elif self.route.is_django():
            return self.request.POST
        elif self.route.is_appengine():
            return self.request.REQUEST
        elif self.route.is_dummy() or self.route.is_standalone():
            return self.request.data
        raise NotImplementedError

    @property
    def REQUEST(self):
        if self.route.is_flask():
            return self.request.args
        elif self.route.is_django():
            return self.request.REQUEST
        elif self.route.is_appengine():
            return dict(map(lambda i: (i, self.request.get(i)), \
                self.request.arguments()))
        elif self.route.is_dummy() or self.route.is_standalone():
            return self.request.data
        raise NotImplementedError

    @property
    def META(self):
        if self.route.is_flask():
            return self.request.environ
        elif self.route.is_django():
            return self.request.META
        
        raise NotImplementedError

    @property
    def remote_addr(self):
        if self.route.is_flask() or self.route.is_django():
            return self.META.get('REMOTE_ADDR')
        elif self.route.is_appengine():
            return self.request.remote_addr
        elif self.route.is_dummy() or self.route.is_standalone():
            return self.request.remote_addr
        raise NotImplementedError

    @property
    def method(self):
        if self.route.is_flask():
            return self.request.method
        elif self.route.is_django():
            return self.request.method
        elif self.route.is_appengine():
            return self.request.method
        elif self.route.is_dummy() or self.route.is_standalone():
            return self.request.method
        raise NotImplementedError