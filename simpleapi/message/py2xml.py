# -*- coding: utf-8 -*-

from xml.etree import cElementTree as ET
import base64

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

    def build_str(self, value):
        element = self.create_item('str')
        element.text = str(value)
        return element

    def build_unicode(self, value):
        element = self.create_item('unicode')
        element.text = value.encode("utf-8")
        return element

    def build_int(self, value):
        element = self.create_item('int')
        element.text = str(int(value))
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
    
    # Parser methods
    
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

    def parse_tuple(self, element):
        tmp = []
        for item in element.getchildren():
            tmp.append(self.handle(item, 'parse'))
        return tuple(tmp)

    def parse_unicode(self, element):
        return element.text.decode("utf-8")

    def parse_str(self, element):
        return element.text

    def parse_int(self, element):
        return int(element.text)

    def parse_float(self, element):
        return float(element.text)

    def parse_bool(self, element):
        return bool(int(element.text))

    # generic methods

    def build(self, value):
        root = self.handle(value)
        return ET.tostring(root)

    def parse(self, value):
        root = ET.fromstring(value)
        return self.handle(root, op='parse')
"""
type_methods = {
    dict: PythonToXML._dump_dict,
    list: PythonToXML._dump_sequence,
    tuple: PythonToXML._dump_sequence,
    set: PythonToXML._dump_sequence,
    frozenset: PythonToXML._dump_sequence,
    str: PythonToXML._dump_string,
    unicode: PythonToXML._dump_string,
    int: PythonToXML._dump_int,
    float: PythonToXML._dump_float,
    hex: PythonToXML._dump_hex,
    bytes: PythonToXML._dump_bytes,
    bool: PythonToXML._dump_bool,
    'dict': [PythonToXML._load_dict, None],
    'list': [PythonToXML._load_sequence, 'list'],
    'tuple': [PythonToXML._load_sequence, 'tuple'],
    'set': [PythonToXML._load_sequence, 'set'],
    'frozenset': [PythonToXML._load_sequence, 'frozenset'],
    'string': [PythonToXML._load_string, None],
    'int': [PythonToXML._load_int, None],
    'float': [PythonToXML._load_float, None],
    'hex': [PythonToXML._load_hex, None],
    'bytes': [PythonToXML._load_bytes, None],
    'bool': [PythonToXML._load_bool, None],
}
"""