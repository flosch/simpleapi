# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *

from simpleapi import Route
from handlers import Calculator

urlpatterns = patterns('',
	(r'^calculator/$', Route(Calculator)),
)