# -*- coding: utf-8 -*-

import client
import server

from client import *
from server import *

__all__ = (client.__all__ + server.__all__)
__author__ = 'Florian Schlachter'

VERSION = (0, 0, 2)

def get_version():
    version = '%s.%s' % (VERSION[0], VERSION[1])
    if VERSION[2]:
        version = '%s.%s' % (version, VERSION[2])
    return version

__version__ = get_version()