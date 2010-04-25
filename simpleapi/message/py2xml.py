# -*- coding: utf-8 -*-

from xml.etree import cElementTree as ET
import base64

__all__ = ('PythonToXML', 'type_methods')

class PythonToXML(object):
    @classmethod
    def dumps(cls, obj):
        el = type_methods[type(obj)](obj)
        return ET.tostring(el)

    @classmethod
    def loads(cls, stream):
        if not ET.iselement(stream):
            stream = ET.fromstring(stream)
        method, arg = type_methods[stream.tag]
        return method(stream, arg)

    @classmethod
    def _dump_dict(cls, obj):
        el = ET.Element('dict')
        for key, value in obj.iteritems():
            e = ET.Element(key)
            e.text = cls.dumps(value)
            el.append(e)

        return el

    @classmethod
    def _dump_sequence(cls, obj):
        type_ = 'list'
        if isinstance(obj, tuple):
            type_ = 'tuple'
        elif isinstance(obj, set):
            type_ = 'set'
        elif isinstance(obj, frozenset):
            type_ = 'frozenset'

        el = ET.Element(type_)
        for item in obj:
            e = ET.Element('item')
            e.text = cls.dumps(item)
            el.append(e)

        return el

    @classmethod
    def _dump_string(cls, obj):
        el = ET.Element('string')
        el.text = obj
        return el

    @classmethod
    def _dump_int(cls, obj):
        el = ET.Element('int')
        el.text = str(obj)
        return el

    @classmethod
    def _dump_float(cls, obj):
        el = ET.Element('float')
        el.text = str(obj)
        return el

    @classmethod
    def _dump_hex(cls, obj):
        el = ET.Element('hex')
        el.text = str(obj)
        return el

    @classmethod
    def _dump_bytes(cls, obj):
        el = ET.Element('bytes')
        el.text = base64.b64encode(obj)
        return el

    @classmethod
    def _load_dict(cls, el, type_=None):
        tmp = {}
        for item in el.getchildren():
            tmp[item.tag] = cls.loads(item.text)

        return tmp

    @classmethod
    def _load_sequence(cls, el, type_='list'):
        tmp = list()
        for item in el.find('item'):
            tmp.append(cls.loads(item))

        if type_ == 'tuple':
            return tuple(tmp)
        elif type_ == 'set':
            return set(tmp)
        elif type_ == 'frozenset':
            return frozenset(tmp)

        return tmp

    @classmethod
    def _load_string(cls, el, type_=None):
        return el.text

    @classmethod
    def _load_int(cls, el, type_=None):
        return int(el.text)

    @classmethod
    def _load_float(cls, el, type_=None):
        return float(el.text)

    @classmethod
    def _load_hex(cls, el, type_=None):
        return hex(el.text)

    @classmethod
    def _load_bytes(cls, el, type_=None):
        return base64.b64decode(el.text)

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
}

