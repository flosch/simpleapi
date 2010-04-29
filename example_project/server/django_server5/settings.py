# -*- coding: utf-8 -*-

import sys
import os

# just for me: :-)
sys.path.append("/Users/flosch/devlibs/3rdparty/")

PROJECT_ROOT = os.path.dirname(__file__)

ROOT_URLCONF = 'django_server5.urls'

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'testdb.db'
    }
}

TIME_ZONE = 'Europe/Berlin'

INSTALLED_APPS = (
    'api',
)

MIDDLEWARE_CLASSES = ()