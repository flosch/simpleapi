# -*- coding: utf-8 -*-

__all__ = ('Client', 'ClientException', 'ConnectionException', 'RemoteException', )

import urllib
import cPickle
import json

class ClientException(Exception): pass
class ConnectionException(ClientException): pass
class RemoteException(ClientException): pass
class Client(object):
	
	def __init__(self, ns, access_key=None, version='default', use_pickle=False):
		self.ns = ns
		self.access_key = access_key
		self.version = version
		self.use_pickle = use_pickle
	
	def _handle_remote_call(self, fname):
		def do_call(**kwargs):
			data = {
				'_call': fname,
				'_output': self.use_pickle and 'pickle' or 'json',
				'_input': self.use_pickle and 'pickle' or 'value',
				'_access_key': self.access_key or '',
				'_version': self.version
			}
			if self.use_pickle:
				for key, value in kwargs.iteritems():
					kwargs[key] = cPickle.dumps(value)

			data.update(kwargs)
			
			try:
				response = urllib.urlopen(self.ns, urllib.urlencode(data)).read()
			except IOError, e:
				raise ConnectionException(e)
			
			try:
				if self.use_pickle:
					try:
						response = cPickle.loads(response)
					except (cPickle.UnpicklingError, EOFError):
						raise ClientException(u'Couldn\'t unpickle response data. Did you added "pickle" to the namespace\'s __features__ list?')
				else:
					response = json.loads(response)
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