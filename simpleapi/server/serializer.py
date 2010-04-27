# -*- coding: utf-8 -*-

try:
    from django.core import serializers
    from django.db.models import Model
    from django.db.models.query import QuerySet
except ImportError, e:
    # FIXME: dirty hack? how can we prevent that the
    # Client library raises an error if django settings isn't present
    if not 'DJANGO_SETTINGS_MODULE' in str(e):
        raise

__all__ = ('ModelSerializer', 'QuerySerializer')

class Serializer(object):
    def __init__(self, obj, **options):
        self.obj = obj
        self.options = options
        self.fields = options.get('fields', [])
        self.excludes = options.get('excludes', [])
        
        assert isinstance(self.fields, (tuple, list))
        assert isinstance(self.excludes, (tuple, list))

class ModelSerializer(Serializer):

    def serialize(self):
        assert isinstance(self.obj, Model)

        result = {}
        for field in self.obj._meta.local_fields:
            pass # TODO
        return result

class QuerySerializer(Serializer):

    def serialize(self):
        assert isinstance(self.obj, QuerySet)

        result = []
        for obj in self.obj:
            model_serializer = ModelSerializer(obj, **self.options)
            result.append(model_serializer.serialize())
        return result