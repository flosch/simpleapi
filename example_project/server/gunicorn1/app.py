import sys
import os

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    '../../../'))
sys.path.append(root)

from simpleapi import Route
from handlers import MyAPI

__all__ = ('route', )

route = Route(MyAPI, framework='wsgi', path=r'^/api/')
print route

# Simply start the server with e. g. 5 workers:
# $ gunicorn -w 5 app:route