# -*- coding: utf-8 -*-

import sys
import os
root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    '../../../'))
sys.path.append(root)

from simpleapi import Client

client = Client(ns='http://localhost:8888/api/', transport_type='xml')

print "Creating new contact..."
print client.new(name=u'Florian Müller', phone='+49 555 444')
print
print "Creating another contact..."
print client.new(name=u'Florian Maier', phone='+49 555 444', fax='+48 444 555')
print
print "Searching for 'Florian'..."
for search_item in client.search(pattern='Florian'):
    print u"Found: %(name)s (phone: %(phone)s, fax: %(fax)s)" % search_item