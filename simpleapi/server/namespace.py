# -*- coding: utf-8 -*-

__all__ = ('Namespace', 'NamespaceException')

class NamespaceException(Exception): pass
class Namespace(object):

    def __init__(self, request):
        self.request = request
        self.session = request.session

    def error(self, errors):
        raise NamespaceException(errors)