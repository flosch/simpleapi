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
            'items': serialize(qs, excludes=['datetime_added',])
        }
    search.published = True
    
    #def demo_inline_model(self, pattern)
    #