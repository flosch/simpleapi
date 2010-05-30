# -*- coding: utf-8 -*-

import sys
import os
root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    '../../../'))
sys.path.append(root)

from simpleapi import Client

client = Client(ns='http://localhost:8888/api/', transport_type='json')

print "Creating new contact..."
print client.new(name=u'Florian Müller', phone='+49 555 444')
print
print "Creating another contact..."
print client.new(name=u'Florian Maier', phone='+49 555 444', fax='+48 444 555')
print
print "Searching for 'Florian'..."
search_result = client.search(pattern='Florian')
print " - Found %s results" % search_result['count']
if search_result['count'] > 4:
    print "(Showing only the first 4 items)"
print

print "First item is:", search_result['first_item']
print

print "Second item is:", search_result['second_item']
print

for search_item in search_result['items'][:4]:
    print u"Found: %(name)s (phone: %(phone)s, fax: %(fax)s)" % search_item