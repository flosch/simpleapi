# -*- coding: utf-8 -*-

import sys
import os

# just for me: :-)
sys.path.append("/Users/flosch/devlibs/3rdparty/")

from mongoengine import connect

PROJECT_ROOT = os.path.dirname(__file__)

ROOT_URLCONF = 'django_server4.urls'

DEBUG = True

# used by simpleapi.features.CacheFeature:
CACHE_BACKEND = 'locmem://'

connect('simpleapi_test')

TIME_ZONE = 'Europe/Berlin'

INSTALLED_APPS = (
    'api',
)

MIDDLEWARE_CLASSES = ()