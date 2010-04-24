# -*- coding: utf-8 -*-

__all__ = ('Namespace', 'NamespaceException')

class NamespaceException(Exception): pass
class Namespace(object):
    
    def error(self, errors):
        raise NamespaceException(errors)