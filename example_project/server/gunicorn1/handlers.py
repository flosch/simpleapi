# -*- coding: utf-8 -*-

from simpleapi import Namespace
import time

class MyAPI(Namespace):
    def add(self, a, b):
        return a + b
    add.published = True
    add.constraints = lambda ns, key, value: int(value)

    def test(self):
        time.sleep(5)
        self.error(u'Yay.')
    test.published = True