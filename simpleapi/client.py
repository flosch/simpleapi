# -*- coding: utf-8 -*-

__all__ = ('Client', 'ClientException', 'ConnectionException', 'RemoteException', )

import urllib
import cPickle
try:
    import json
except ImportError:
    import simplejson as json

from xml.parsers.expat import ExpatError

from response import Response

class ClientException(Exception): pass
class ConnectionException(ClientException): pass
class RemoteException(ClientException): pass
class Client(object):

    def __init__(self, ns, access_key=None, version='default',
                 use_pickle=False, output='json'):
        self.ns = ns
        self.access_key = access_key
        self.version = version
        self.output = use_pickle and 'pickle' or output
        self.input = use_pickle and 'pickle' or 'value'

    def _handle_remote_call(self, fname):
        def do_call(**kwargs):
            data = {
                '_call': fname,
                '_output': self.output,
                '_input': self.input,
                '_access_key': self.access_key or '',
                '_version': self.version
            }
            if self.output == 'pickle':
                for key, value in kwargs.iteritems():
                    kwargs[key] = cPickle.dumps(value)

            data.update(kwargs)

            try:
                response = urllib.urlopen(self.ns, urllib.urlencode(data)).read()
            except IOError, e:
                raise ConnectionException(e)

            try:
                if self.output == 'pickle':
                    try:
                        response = cPickle.loads(response)
                        return response.get('result')
                    except (cPickle.UnpicklingError, EOFError):
                        raise ClientException(u'Couldn\'t unpickle response data. Did you added "pickle" to the namespace\'s __features__ list?')
                elif self.output == 'json':
                    response = json.loads(response)
                    if response.get('sucess'):
                        response = response.get('result')
                        if response.get('simpleapi') == 'response':
                            return Response.parse_json(response)

                        return response
                    else:
                        raise RemoteException(". ".join(response.get('errors')))
                elif self.output == 'xml':
                    try:
                        return Response.parse_xml(response)
                    except ExpatError:
                        raise RemoteException(". ".join(response.get('errors')))
            except ValueError, e:
                raise ConnectionException, e

            if self.output == 'json' and response.get('success'):
                ret = response.get('result')
                if '__type__' in ret:
                    ret = Response.parse_json(ret)
                return ret
            else:
                raise RemoteException(". ".join(response.get('errors')))

        return do_call

    def __getattr__(self, name):
        return self._handle_remote_call(name)

    def set_version(self, version):
        self.version = int(version)

    def set_ns(self, ns):
        self.ns = ns
