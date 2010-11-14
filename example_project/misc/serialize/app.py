from mongoengine import connect
import sys
import os
import time

connect('simpleapitest')

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    '../../../'))
sys.path.append(root)

from simpleapi import Route, DummyClient, RemoteException
from handlers import MyAPI

client = DummyClient(Route(MyAPI, framework='dummy'))
print "Add?", client.add()
print "Get?", client.get()