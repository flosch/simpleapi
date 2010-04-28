# -*- coding: utf-8 -*-

import datetime

from mongoengine import *

class DetailedInformation(EmbeddedDocument):
    status = StringField(choices=('sent', 'failed', 'progress'), default='progress')    

class Contact(Document):
    
    name = StringField()
    phone = StringField()
    fax = StringField()
    datetime_added = DateTimeField(default=datetime.datetime.now)
    
    details = EmbeddedDocumentField(DetailedInformation,
                                    default=DetailedInformation)
    
    testdict = DictField()