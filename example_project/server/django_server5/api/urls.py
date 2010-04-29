# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *

from simpleapi import Route
from handlers import ContactAPI

urlpatterns = patterns('',
    (r'^$', Route(ContactAPI, restful=True)),
    (r'^(?P<id>[\d]+)/$', Route(ContactAPI, restful=True)),
)