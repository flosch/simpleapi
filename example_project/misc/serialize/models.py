# -*- coding: utf-8 -*-

from datetime import datetime
from mongoengine import *

class TestItem2(EmbeddedDocument):
    name = StringField()
    type = StringField()
    typespecific = DictField(default={})
 
class Entry(EmbeddedDocument):
    created = DateTimeField(default=datetime.now())
 
class StringEntry(Entry):
    value = StringField()
 
class InfoDoc(EmbeddedDocument):
    title = StringField()
    created = DateTimeField(default=datetime.now())

class Table(Document):
    info    = EmbeddedDocumentField(InfoDoc)
    schema  = ListField(EmbeddedDocumentField(TestItem2))
    entries = ListField(EmbeddedDocumentField(Entry))
