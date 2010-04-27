# -*- coding: utf-8 -*-

import re
from simpleapi import Namespace, Feature

from models import Contact

class ContactAPI(Namespace):
    
    def new(self, name, phone=None, fax=None):
        contact = Contact.objects.create(
            name=name,
            phone=phone,
            fax=fax
        )
        return contact
    new.published = True

    def search(self, pattern):
        return Contact.objects.filter(
            name__icontains=pattern
        )
    search.published = True