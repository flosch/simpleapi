try:
    import json
except ImportError:
    import simplejson as json

from simpleapi.message import formatters, Formatter, PythonToXML

from message import Message

class JSONFormatter(Formatter):
    __mime__ = "application/json"

    def build(self, value):
        if not isinstance(value, Message):
            raise TypeError('You MUST use a Message to build your response')
        return value.to_json(as_dict=False)

    def kwargs(self, value, action='build'):
        if action == 'build':
            return json.dumps(value)
        elif action == 'parse':
            return json.loads(value)

    def parse(self, value):
        return Message.parse_json(value)

class JSONPFormatter(Formatter):
    __mime__ = "application/javascript"

    def build(self, value):
        if not isinstance(value, Message):
            raise TypeError('You MUST use a Message to build your response')

        func = self.callback or 'simpleapiCallback'
        return u'%(func)s(%(data)s)' % {'func': func,
                                        'data': value.to_json(as_dict=False)}

    def kwargs(self, value, action='build'):
        if action == 'build':
            return json.dumps(value)
        elif action == 'parse':
            return json.loads(value)

    def parse(self, value):
        return Message.parse_json(value)

class XMLFormatter(Formatter):
    __mime__ = "application/xml"

    def build(self, value):
        if not isinstance(value, Message):
            raise TypeError('You MUST use a Message to build your response')

        return value.to_xml()

    def kwargs(self, value, action='build'):
        if action == 'build':
            return PythonToXML().build(value)
        elif action == 'parse':
            return PythonToXML().parse(value)

    def parse(self, value):
        return Message.parse_xml(value)

formatters.register('json', JSONFormatter, override=True)
formatters.register('jsonp', JSONPFormatter, override=True)
formatters.register('xml', XMLFormatter, override=True)