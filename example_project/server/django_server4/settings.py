# -*- coding: utf-8 -*-

import sys
import os

# just for me: :-)
sys.path.append("/Users/flosch/devlibs/3rdparty/")

PROJECT_ROOT = os.path.dirname(__file__)

ROOT_URLCONF = 'django_server3.urls'

DEBUG = True

# used by simpleapi.features.CacheFeature:
CACHE_BACKEND = 'locmem://'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'testdb.db'
    }
}

#
# Language / localization
#

TIME_ZONE = 'Europe/Berlin'

INSTALLED_APPS = (
    'api',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.request",
    "django.core.context_processors.auth",
)

#
# Secret key
#

try:
    SECRET_KEY
except NameError:
    SECRET_FILE = os.path.join(PROJECT_ROOT, 'secret.txt')
    try:
        SECRET_KEY = open(SECRET_FILE).read().strip()
    except IOError:
        try:
            from random import choice
            SECRET_KEY = ''.join([choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50)])
            secret = file(SECRET_FILE, 'w')
            secret.write(SECRET_KEY)
            secret.close()
        except IOError:
            Exception('Please create a %s file with random characters to generate your secret key!' % SECRET_FILE)