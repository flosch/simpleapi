# -*- coding: utf-8 -*-

import urllib

from simpleapi import Namespace

class MyAPI(Namespace):
    def add_one(self, a, b):
        # Raises an error since c doesn't exist (thanks to debug=True in the
        # Route configuration the python debugger will came up for debugging)
        a = c + 1
        return a + b
    add_one.published = True
    add_one.constraints = lambda ns, key, val: int(val)

    def download(self, url):
        return urllib.urlopen(url).read()
    download.published = True