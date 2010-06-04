import sys
import os

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    '../../../'))
sys.path.append(root)

from simpleapi import Route, DummyClient, RemoteException
from handlers import MyAPI

"""
Let's assume we want access our in-app API. This is what DummyClient is for.
"""

client = DummyClient(Route(MyAPI, framework='dummy'),
                     access_key='secret key')
print "5 + 2 =", client.add(a=5, b=2)
try:
    print client.test()
except RemoteException, e:
    print "Remote exception raised:", unicode(e)