import sys
import os
import time

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    '../../../'))
sys.path.append(root)

from simpleapi import Route, DummyClient, RemoteException
from handlers import MyAPI

client = DummyClient(Route(MyAPI, framework='dummy'))
for i in xrange(5):
    try:
        print len(client.download(url="http://www.pizzabus.de"))
    except RemoteException, e:
        print "Failure during request:", e
        time.sleep(.5)