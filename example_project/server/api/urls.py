# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *

from simpleapi import Route
from handlers import OldCalculator, NewCalculator, SomeFunctions, Misc

urlpatterns = patterns('',
	(r'^calculator/multiple/$', Route(OldCalculator, NewCalculator)),
	(r'^calculator/one/$', Route(OldCalculator)),
	(r'^functions/$', Route(SomeFunctions)),
	(r'^misc/$', Route(Misc))
)