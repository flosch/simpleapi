# -*- coding: utf-8 -*-

import time
import urllib

from simpleapi import Namespace, serialize

from models import *

class MyAPI(Namespace):
    def add(self):
        schema = [TestItem2(name='field1', type='string'),
            TestItem2(name='field2', type='string') ]

        info = InfoDoc(title='testtitel', owner='myTitle')
        m = Table(info=info, schema=schema)
        m.save()
        return m
    add.published = True

    def get(self):
        t = Table.objects[Table.objects.count()-1]
        return t.info
    get.published = True