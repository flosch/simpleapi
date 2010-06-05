import sys
import os

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    '../../../'))
sys.path.append(root)

from simpleapi import Route, DummyClient, RemoteException
from handlers import MyAPI

client = DummyClient(Route(MyAPI, framework='dummy', debug=True))
try:
    client.add_one(a=1, b=5)
except RemoteException, e:
    print "Exception raised:", e
client.download(url="http://www.pizzabus.de")