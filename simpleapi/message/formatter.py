# -*- coding: utf-8 -*-

import cPickle
try:
    import json
except ImportError:
    import simplejson as json

from py2xml import PythonToXML

__all__ = ('formatters', 'Formatter')

class FormattersSingleton(object):
    _formatters = {}

    def __new__(cls):
        it = cls.__dict__.get("__it__")
        if it is not None:
            return it
        cls.__it__ = it = object.__new__(cls)
        return it

    def register(self, name, formatter, override=False):
        """
            Register the given formatter
        """
        if not isinstance(formatter(None, None), Formatter):
            raise TypeError("You can only register a Formatter not a {item}".format(item=formatter))

        if name in self._formatters and not override:
            raise AttributeError("{name} is already a valid format type, try a new name".format(name=name))

        self._formatters[name] = formatter

    def copy(self):
        return dict(**self._formatters)

    def __contains__(self, value):
        return value in self._formatters

    def __getitem__(self, name):
        return self._formatters.get(name)

    def __setitem__(self, *args):
        raise AttributeError

formatters = FormattersSingleton()

class Formatter(object):

    def __init__(self, http_request, callback):
        self.http_request = http_request
        self.callback = callback

    def build(self, value):
        raise NotImplemented

    def kwargs(self, value, action='build'):
        raise NotImplemented

    def parse(self, value):
        raise NotImplemented

class JSONFormatter(Formatter):
    __mime__ = "application/json"

    def build(self, value):
        return json.dumps(value)

    def kwargs(self, value, action='build'):
        if action == 'build':
            return self.build(value)
        elif action == 'parse':
            return self.parse(value)

    def parse(self, value):
        return json.loads(value)

class JSONPFormatter(Formatter):
    __mime__ = "application/javascript"

    def build(self, value):
        func = self.callback or 'simpleapiCallback'
        return u'{func}({data})'.format(func=func, data=json.dumps(value))

    def kwargs(self, value):
        if action == 'build':
            return json.dumps(value)
        elif action == 'parse':
            return self.parse(value)

    def parse(self, value):
        return json.loads(value)

class ValueFormatter(Formatter):
    __mime__ = "text/html"

    def build(self, value):
        return value

    def kwargs(self, value, action='build'):
        if action == 'build':
            return self.build(value)
        elif action == 'parse':
            return self.parse(value)

    def parse(self, value):
        return unicode(value)

class PickleFormatter(Formatter):
    __mime__ = "application/octet-stream"

    def build(self, value):
        return cPickle.dumps(value)

    def kwargs(self, value, action='build'):
        if action == 'build':
            return self.build(value)
        elif action == 'parse':
            return self.parse(value)

    def parse(self, value):
        if isinstance(value, unicode):
            value = value.encode("utf-8")
        return cPickle.loads(value)

class XMLFormatter(Formatter):
    __mime__ = "text/xml"

    def build(self, value):
        return PythonToXML.dumps(value)

    def kwargs(self, value, action='build'):
        if action == 'build':
            return self.build(value)
        elif action == 'parse':
            return self.parse(value)

    def parse(self, value):
        return PythonToXML.loads(value)

formatters.register('json', JSONFormatter)
formatters.register('jsonp', JSONPFormatter)
formatters.register('value', ValueFormatter)
formatters.register('pickle', PickleFormatter)
formatters.register('xml', XMLFormatter)
