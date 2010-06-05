import sys
import os

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    '../../../'))
sys.path.append(root)

from simpleapi import Route
from handlers import MyAPI

route = Route(MyAPI, framework='standalone', path=r'^/api/')
route.serve() # start the WSGI Server on Port 5050