# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *

from simpleapi import Route
from handlers import Example

from sapi import formatters, wrappers

urlpatterns = patterns('',
    (r'^example/$', Route(Example, debug=True))
)