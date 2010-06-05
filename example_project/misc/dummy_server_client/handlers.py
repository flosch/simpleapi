# -*- coding: utf-8 -*-

from simpleapi import Namespace

class MyAPI(Namespace):
    __authentication__ = lambda ns, key: key == "secret key"
    
    def add(self, a, b):
        return a + b
    add.published = True
    add.constraints = lambda ns, key, value: int(value)

    def test(self):
        self.error(u'This is an exception.')
    test.published = True