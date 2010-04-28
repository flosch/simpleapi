# -*- coding: utf-8 -*-

__all__ = ('Client', 'ClientException', 'ConnectionException', 'RemoteException', )

import socket
import urllib
import cPickle
from simpleapi.message import formatters, wrappers

class ClientException(Exception): pass
class ConnectionException(ClientException): pass
class RemoteException(ClientException): pass
class Client(object):
    """simpleapi's client library. 
    
    :param ns: URL of your :class:`~simpleapi.Route`'s endpoint
    :param access_key: string key used for authentication
    :param version: Namespace version to be used (default is highest)
    :param transport_type: encoding/decoding type for request/response (default
                           is json)
    :param wrapper_type: wrapper used for formatting the response
    :param timeout: connection timeout in secs (default is system parameter)
    """

    def __init__(self, ns, access_key=None, version='default',
                 transport_type='json', wrapper_type='default', timeout=None):

        if timeout is not None:
            socket.setdefaulttimeout(timeout)

        self.ns = ns
        self.access_key = access_key
        self.version = version

        assert transport_type in formatters
        self.transport_type = transport_type

        assert wrapper_type in wrappers
        self.wrapper_type = wrapper_type

    def _handle_remote_call(self, fname):
        def do_call(**kwargs):
            data = {
                '_call': fname,
                '_output': self.transport_type,
                '_input': self.transport_type,
                '_wrapper': self.wrapper_type,
                '_access_key': self.access_key or '',
                '_version': self.version
            }

            formatter = formatters[self.transport_type](None, None)

            for key, value in kwargs.iteritems():
                kwargs[key] = formatter.kwargs(value)

            data.update(kwargs)

            try:
                response = urllib.urlopen(self.ns,
                                          urllib.urlencode(data))

                assert response.getcode() in [200,], \
                    u'HTTP-Server returned http code %s (expected: 200) ' % \
                    response.getcode()

                response_buffer = response.read()
            except IOError, e:
                raise ConnectionException(e)

            try:
                response = formatter.parse(response_buffer)
            except (cPickle.UnpicklingError, EOFError), e:
                raise ClientException(
                    u'Couldn\'t unpickle response ' \
                    'data. Did you added "pickle" to the namespace\'s' \
                    ' __features__ list?'
                )
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

    def set_ns(self, ns):
        """changes the URL for the Route's endpoint"""
        self.ns = ns