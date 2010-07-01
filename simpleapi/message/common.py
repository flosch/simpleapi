# -*- coding: utf-8 -*-

try:
    import json
except ImportError:
    try:
        from django.utils import simplejson as json
    except Exception, e:
        import simplejson as json

__all__ = ('json', )