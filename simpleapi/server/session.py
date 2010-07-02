# -*- coding: utf-8 -*-

__all__ = ('Session', )

class SessionObj(object): pass

class Session(object):
    def __init__(self):
        self._internal = SessionObj()

    def clear(self):
        for key in self.__dict__.keys():
            if not key.startswith('_'):
                del self.__dict__[key]