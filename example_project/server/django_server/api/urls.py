# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *

from simpleapi import Route
from handlers import OldCalculator, NewCalculator, SomeFunctions, Misc

urlpatterns = patterns('',
    (r'^calculator/multiple/$', Route(OldCalculator, NewCalculator, debug=True)),
    (r'^calculator/one/$', Route(OldCalculator, debug=True)),
    (r'^functions/$', Route(SomeFunctions, debug=True)),
    (r'^misc/$', Route(Misc))
)