# -*- coding: utf-8 -*-

__all__ = ('Client', 'ClientException', 'ConnectionException', 'RemoteException', )

import urllib
import cPickle

try:
    import json
except ImportError:
    import simplejson as json

from simpleapi.message import formatters, wrappers

class ClientException(Exception): pass
class ConnectionException(ClientException): pass
class RemoteException(ClientException): pass
class Client(object):

    def __init__(self, ns, access_key=None, version='default',
                 transport_type='json', wrapper_type='default'):
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
                response = urllib.urlopen(self.ns, urllib.urlencode(data)).read()
            except IOError, e:
                raise ConnectionException(e)

            try:
                response = formatter.parse(response)
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
        self.version = int(version)

    def set_ns(self, ns):
        self.ns = ns