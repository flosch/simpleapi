# -*- coding: utf-8 -*-

import re
from simpleapi import Namespace, Feature, serialize

from models import Contact

class ContactAPI(Namespace):

    def new(self, name, phone=None, fax=None):
        contact = Contact.objects.create(
            name=name,
            phone=phone,
            fax=fax
        )
        return serialize(contact, excludes=[re.compile(r'^datetime_'),])
    new.published = True

    def search(self, pattern):
        qs = Contact.objects.filter(
            name__icontains=pattern
        )
        return {
            'count': qs.count(),
            
            # use serialize if you want to exclude or define fields
            'items': serialize(qs, excludes=['datetime_added',]), 
            
            # inline objects are no problem without serialize
            'first_item': (qs.count() > 0) and qs[0] or None,
            
            # define fields if you want to restrict output to specific fields
            'second_item': (qs.count() > 1) and \
                serialize(qs[1], fields=[re.compile('^name')]) or None
        }
    search.published = True