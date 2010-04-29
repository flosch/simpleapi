# -*- coding: utf-8 -*-

import re
from simpleapi import Namespace, Feature, serialize

from models import Contact

class ContactAPI(Namespace):
    def get(self, id):
        return Contact.objects.get(id=id)
    get.constraints = {'id': int}
    get.published = True

    def post(self, name, phone=None, fax=None):
        return Contact.objects.create(
            name=name,
            phone=phone,
            fax=fax
        )
    post.published = True