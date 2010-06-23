import sys
import os
os.environ['SIMPLEAPI_DEBUG'] = '1' # activate simpleapi-wide debug
os.environ['SIMPLEAPI_DEBUG_LEVEL'] = 'call' # either call (for profiling every call) or all (for profiling all calls accumulated)

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    '../../../'))
sys.path.append(root)

from simpleapi import Route, DummyClient, RemoteException
from handlers import MyAPI

client = DummyClient(Route(MyAPI, framework='dummy'))
for i in xrange(3):
    client.add_one(a=1, b=5)