# -*- coding: utf-8 -*-

from xml.etree import cElementTree as ET
import base64
from dateutil.parser import parse

__all__ = ('PythonToXML',)

class PythonToXML(object):
    def handle(self, value, op='build'):
        if op == 'build':
            return getattr(self, 'build_%s' % type(value).__name__)(value)
        elif op == 'parse':
            type_name = value.get('type')
            return getattr(self, 'parse_%s' % type_name)(value)

    def create_item(self, type_name):
        element = ET.Element('item')
        element.set('type', type_name)
        return element

    # Builder methods

    def build_NoneType(self, value):
        element = self.create_item('NoneType')
        return element

    def build_time(self, value):
        element = self.create_item('time')
        element.text = value.isoformat()
        return element

    def build_date(self, value):
        element = self.create_item('date')
        element.text = value.isoformat()
        return element

    def build_datetime(self, value):
        element = self.create_item('datetime')
        element.text = value.ctime()
        return element

    def build_str(self, value):
        element = self.create_item('str')
        element.text = str(value)
        return element

    def build_unicode(self, value):
        element = self.create_item('unicode')
        element.text = value #.encode("utf-8")
        return element

    def build_int(self, value):
        element = self.create_item('int')
        element.text = str(int(value))
        return element

    def build_long(self, value):
        element = self.create_item('long')
        element.text = str(long(value))
        return element

    def build_float(self, value):
        element = self.create_item('float')
        element.text = str(float(value))
        return element

    def build_bool(self, value):
        element = self.create_item('bool')
        element.text = str(int(value))
        return element

    def build_list(self, value):
        root = self.create_item('list')
        for item in value:
            root.append(self.handle(item))
        return root

    def build_tuple(self, value):
        root = self.create_item('tuple')
        for item in value:
            root.append(self.handle(item))
        return root

    def build_dict(self, value):
        root = self.create_item('dict')
        for key, value in value.iteritems():
            element = self.handle(value)
            element.set('name', key)
            root.append(element)
        return root

    def build_set(self, value):
        root = self.create_item('set')
        for item in list(value):
            root.append(self.handle(item))
        return root

    # Parser methods

    def parse_datetime(self, element):
        return parse(element.text)

    def parse_date(self, element):
        return parse(element.text).date()

    def parse_time(self, element):
        return parse(element.text).time()

    def parse_dict(self, element):
        tmp = {}
        for item in element.getchildren():
            tmp[item.get('name')] = self.handle(item, 'parse')
        return tmp

    def parse_list(self, element):
        tmp = []
        for item in element.getchildren():
            tmp.append(self.handle(item, 'parse'))
        return tmp

    def parse_set(self, element):
        tmp = []
        for item in element.getchildren():
            tmp.append(self.handle(item, 'parse'))
        return set(tmp)

    def parse_tuple(self, element):
        tmp = []
        for item in element.getchildren():
            tmp.append(self.handle(item, 'parse'))
        return tuple(tmp)

    def parse_unicode(self, element):
        return element.text

    def parse_str(self, element):
        return element.text

    def parse_int(self, element):
        return int(element.text)

    def parse_long(self, element):
        return long(element.text)

    def parse_float(self, element):
        return float(element.text)

    def parse_bool(self, element):
        return bool(int(element.text))

    def parse_NoneType(self, element):
        return None

    # generic methods

    def build(self, value):
        root = self.handle(value)
        return ET.tostring(root)

    def parse(self, value):
        root = ET.fromstring(value)
        return self.handle(root, op='parse')