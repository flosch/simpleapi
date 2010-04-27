import sys
import os
root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    '../../../'))
sys.path.append(root)

from sapi import formatters, wrappers

from simpleapi import Client

def run(output='json'):
    example = Client(ns='http://127.0.0.1:8888/api/example/', version=1,
                     transport_type=output, wrapper_type='message')

    #messages should be a Message object, which is models after ElementTree
    messages = example.test(username=u'Digitalxero')

    print "Messages for:", messages.to
    for msg in messages.findall('message'):
        print "    Message From:", msg.get('from')
        print "        ", msg.text

print "Using JSON"
run()
print
print "Using XML"
run('xml')

