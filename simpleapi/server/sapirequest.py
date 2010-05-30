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
            if route.framework == 'flask':
                assert has_flask
                request = flask_request
                framework = 'flask'
            else:
                raise ValueError(u'HttpRequest-object is missing')
        else:
            framework = 'django'

        self.framework = framework
        self.request = request

    def is_flask(self):
        return self.framework == 'flask'

    def is_django(self):
        return self.framework == 'django'

    @property
    def GET(self):
        if self.framework == 'flask':
            return self.request.args
        elif self.framework == 'django':
            return self.request.GET

    @property
    def POST(self):
        if self.framework == 'flask':
            return self.request.args
        elif self.framework == 'django':
            return self.request.POST

    @property
    def REQUEST(self):
        if self.framework == 'flask':
            return self.request.args
        elif self.framework == 'django':
            return self.request.REQUEST

    @property
    def META(self):
        if self.framework == 'flask':
            return self.request.environ
        elif self.framework == 'django':
            return self.request.META

    @property
    def method(self):
        if self.framework == 'flask':
            return self.request.method
        elif self.framework == 'django':
            return self.request.method