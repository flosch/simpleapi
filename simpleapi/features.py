# -*- coding: utf-8 -*-

__all__ = ('__builtin_features__', 'NamespaceFeature', )

import cPickle

class NamespaceFeature(object):
	
	def __init__(self, route, namespace):
		self.route = route
		self.namespace = namespace
	
	def _setup(self):
		if hasattr(self, 'setup'):
			self.setup()
	
	def _request(self, function_name, function_arguments):
		self.request()
	
	def _response(self, data):
		self.response()

class PickleFeature(NamespaceFeature):
	
	__name__ = "pickle"
	
	def setup(self):
		
		class PickleType(object):

			__mime__ = "application/octet-stream"

			def build(self, data, callback):
				return cPickle.dumps(data)
			
			def parse(self, data):
				return cPickle.loads(data.encode("utf-8"))
		
		self.route.__response_types__['pickle'] = PickleType()
		self.route.__request_types__['pickle'] = PickleType()
	
	def request(self):
		pass # TODO
	
	def response(self):
		pass # TODO

__builtin_features__ = {
	'pickle': PickleFeature
}