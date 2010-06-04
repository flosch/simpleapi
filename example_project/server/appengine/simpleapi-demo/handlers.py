# -*- coding: utf-8 -*-

from simpleapi import Namespace

class MyAPI(Namespace):
    def add(self, a, b):
        return a + b
    add.published = True
    add.constraints = lambda ns, key, value: int(value)

    def get_method(self):
        return self.session.request.method
    get_method.published = True