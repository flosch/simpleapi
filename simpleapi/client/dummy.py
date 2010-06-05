# -*- coding: utf-8 -*- 

from simpleapi.message import formatters
from simpleapi.client import ConnectionException, RemoteException

__all__ = ('DummyClient', )

TRANSPORT_TYPE = 'json'

class DummyRequest(object): pass
class DummyClientException(Exception): pass
class DummyClient(object):
    
    def __init__(self, route, version='default', access_key=None):
        self.route = route
        self.access_key = access_key
        self.version = version

    def _handle_remote_call(self, fname):
        def do_call(**kwargs):
            data = {
                '_call': fname,
                '_access_key': self.access_key or '',
                '_version': self.version,
                '_input': TRANSPORT_TYPE,
                '_output': TRANSPORT_TYPE
            }

            formatter = formatters[TRANSPORT_TYPE](None, None)

            for key, value in kwargs.iteritems():
                kwargs[key] = formatter.kwargs(value)

            data.update(kwargs)
            
            # Build DummyRequest
            request = DummyRequest()
            request.method = 'POST'
            request.data = data
            request.remote_addr = '127.0.0.1'
            
            # Do request
            response_buffer = self.route(request)

            try:
                response = formatter.parse(response_buffer['result'])
            except ValueError, e:
                raise ConnectionException, e

            if response.get('success'):
                return response.get('result')
            else:
                raise RemoteException(". ".join(response.get('errors')))

        return do_call

    def __getattr__(self, name):
        return self._handle_remote_call(name)

    def set_version(self, version):
        """uses a different version for further requests"""
        self.version = int(version)