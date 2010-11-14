# -*- coding: utf-8 -*-

import time
import urllib

from simpleapi import Namespace, serialize

from models import *

class MyAPI(Namespace):
    def add(self):
        schema = [SchemaItem(name='field1', type='string'),
            SchemaItem(name='field2', type='string') ]

        info = TableInfo(title='testtitel', owner='myTitle')
        m = Table(info=info, schema=schema)
        m.save()
    add.published = True
    
    def get(self):
        t = Table.objects.only("info")[Table.objects.count()-1]
        return t
    get.published = True