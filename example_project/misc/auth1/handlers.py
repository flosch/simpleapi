# -*- coding: utf-8 -*-

import time
import urllib

from simpleapi import Namespace

class MyAPI(Namespace):
    __authentication__ = 'auth_access'

    def auth_access(self, access_key):
        if (int(time.time()) % 2) == 0:
            self.error(u'No access - no no!')
        return True

    def download(self, url):
        return urllib.urlopen(url).read()
    download.published = True