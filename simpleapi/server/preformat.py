# -*- coding: utf-8 -*-

try:
    from django.db.models import Model
    from django.db.models.query import QuerySet
    has_django = True
except:
    has_django = False

try:
    import mongoengine
    has_mongoengine = True
except ImportError:
    has_mongoengine = False

from serializer import SerializedObject

__all__ = ()

class Preformatter(object):
    def handle_value(self, value):
        if getattr(type(value), '__name__', 'n/a') == 'dict':
            return self.handle_dict(value)
        elif getattr(type(value), '__name__', 'n/a') == 'list':
            return self.handle_list(value)
        else:
            return self.parse_value(value)

    def parse_value(self, value):
        if has_django and isinstance(value, (Model, QuerySet)):
            value = SerializedObject(value)

        if has_mongoengine and isinstance(value, (mongoengine.Document, \
            mongoengine.queryset.QuerySet)):
            value = SerializedObject(value)

        if isinstance(value, SerializedObject):
            return value.to_python()

        return value

    def handle_list(self, old_list):
        new_list = []
        for item in old_list:
            new_list.append(self.handle_value(item))
        return new_list

    def handle_dict(self, old_dict):
        new_dict = {}
        for key, value in old_dict.iteritems():
            new_dict[key] = self.handle_value(value)
        return new_dict

    def run(self, result):
        return self.handle_value(result)