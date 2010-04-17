# -*- coding: utf-8 -*-

__all__ = ('Client', )

import urllib
import json

class Result(object):
	
	def __init__(self, client, fname, request, response):
		self.client = client
		self.fname = fname
		self.request = request
		self.response = response
	
	def __get__(self, instance, owner):
		print instance, owner
	
	def __repr__(self):
		return '%s:%s' % (self.client.ns, self.fname)

class ClientException(Exception): pass
class ConnectionException(ClientException): pass
class RemoteException(ClientException): pass
class Client(object):
	
	def __init__(self, ns, transport_type='json'):
		self.ns = ns
		self.transport_type = transport_type
	
	def _handle_remote_call(self, fname):
		def do_call(**kwargs):
			data = {
				'_call': fname,
				'_type': self.transport_type,
			}
			data.update(kwargs)
			print data
			try:
				response = urllib.urlopen(self.ns, urllib.urlencode(data)).read()
			except IOError, e:
				raise ConnectionException(e)
			
			try:
				response = json.loads(response)
			except ValueError, e:
				raise ConnectionException, e
			
			if response.get('success'):
				return Result(
					self,
					fname,
					kwargs,
					response
				)				
			else:
				raise RemoteException(". ".join(response.get('errors')))
			
		return do_call
	
	def __getattr__(self, name):
		return self._handle_remote_call(name)