# -*- coding: utf-8 -*-

from simpleapi import Namespace

class MyAPI(Namespace):
    def add(self, a, b):
        return a + b
    add.published = True
    add.constraints = lambda ns, key, value: int(value)

    def test(self):
        self.error(u'Yay.')
    test.published = True