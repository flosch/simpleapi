# -*- coding: utf-8 -*-

__all__ = ('Client', )

import urllib
import cPickle

class ClientException(Exception): pass
class ConnectionException(ClientException): pass
class RemoteException(ClientException): pass
class Client(object):
	
	def __init__(self, ns, access_key=None, version='default'):
		self.ns = ns
		self.access_key = access_key
		self.version = version
	
	def _handle_remote_call(self, fname):
		def do_call(**kwargs):
			data = {
				'_call': fname,
				'_type': 'pickle',
				'_access_key': self.access_key or '',
				'_version': self.version
			}
			data.update(kwargs)
			
			try:
				response = urllib.urlopen(self.ns, urllib.urlencode(data)).read()
			except IOError, e:
				raise ConnectionException(e)
			
			try:
				response = cPickle.loads(response)
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