# -*- coding: utf-8 -*-

__all__ = ('Namespace', 'Route')

import json
import inspect

from django.conf import settings
from django.http import HttpResponse

from utils import glob_list

class NamespaceException(Exception): pass
class Namespace(object):
	
	def error(self, err_or_list):
		raise ResponseException(err_or_list)

class JSONResponse(object):
	
	def build(self, data):
		return json.dumps(data)

class XMLResponse(object):
	
	def build(self, data):
		raise NotImplemented

class RouteException(Exception): pass
class ResponseException(RouteException): pass

class Route(object):
	
	__response_types__ = {
		'json': JSONResponse(),
		'xml': XMLResponse()
	}
	
	def __init__(self, namespace):
		self.namespace = namespace()
		functions = filter(lambda fn: '__' not in fn[0], dict(inspect.getmembers(namespace)).items())
		self.functions = filter(lambda fn: getattr(fn[1], 'published', False) is True, functions)
		self.functions = map(lambda item: (item[0], {'fn': item[1], 'vars': inspect.getargspec(item[1])}), self.functions)
		self.functions = dict(self.functions)
		
		# make glob list from ip address ranges
		if hasattr(self.namespace, '__ip_restriction__'):
			self.namespace.__ip_restriction__ = glob_list(self.namespace.__ip_restriction__)
	
	def _build_response(self, data=None, response_type='json', errors=None, success=None):
		result = {}
		
		if errors is not None:
			result['errors'] = isinstance(errors, list) and errors or [unicode(errors),]
		
		if success is None:
			success = errors is None
		result['success'] = success
		
		if data is not None:
			result['result'] = data
		
		return HttpResponse(
			self.__response_types__[response_type].build(result)
		)
	
	def _handle_request(self, request, fname, rvars):
		if fname not in self.functions.keys():
			raise ResponseException(u'Method (%s) not found' % fname)
		
		fitem = self.functions[fname]
		func = fitem['fn']
		
		# check methods
		if hasattr(func, 'methods'):
			assert isinstance(func.methods, tuple)
			if request.method not in func.methods:
				raise ResponseException(u'HTTP-method not supported (supported: %s)' % ", ".join(func.methods))

		args = []
		kwargs = {}
		
		# var arguments
		if fitem['vars'][3] is not None:
			var_args = fitem['vars'][0][1:-len(fitem['vars'][3])]
		else:
			var_args = fitem['vars'][0][1:]
		
		for arg in var_args:
			try:
				args.append((arg, rvars.pop(arg)))
			except KeyError:
				raise ResponseException(u'Argument %s is missing' % arg)
		
		# optional arguments
		if fitem['vars'][3]:
			for arg in fitem['vars'][0][-len(fitem['vars'][3]):]:
				try:
					kwargs[arg] = rvars.pop(arg)
				except KeyError:
					pass

		# are there any vars left? if true, they are only allowed when func takes **kwargs
		if len(rvars) > 0 and fitem['vars'][2] is None:
			raise ResponseException(u'Unused argument(s): %s' % ", ".join(rvars.keys()))
		
		# update kwargs if func takes **kwargs
		if fitem['vars'][2] is not None:
			kwargs.update(rvars)
		
		# ensure types
		if hasattr(func, 'types'):
			assert isinstance(func.types, dict)
			
			for var_name, var_type in func.types.iteritems():
				if var_name not in fitem['vars'][0]:
					raise ValueError(u'%s not found in function argument list' % var_name)
				
				def convert(value, vtype):
					try:
						if vtype == bool:
							return vtype(int(value))
						else:
							return vtype(value)
					except:
						raise ResponseException(u'Argument %s must be of type %s' % (var_name, repr(vtype)))
				
				new_args = []
				for key, value in args:
					if key == var_name:
						new_args.append((key, convert(value, var_type)))
					else:
						new_args.append((key, value))
				
				args = new_args
				
				for key, value in kwargs.iteritems():
					if key == var_name:
						kwargs[key] = convert(value, var_type)
		
		try:
			args = map(lambda i: i[1], args)
			result = func(self.namespace, *args, **kwargs)
		except Exception, e:
			if settings.DEBUG: raise
			# TODO: send traceback!
			raise ResponseException(u'An internal error occurred during your request. ' \
									 'The technicians have been informed.')
		
		return result
	
	def __call__(self, request):
		rvars = dict(request.REQUEST.iteritems())
		
		# check authentication
		if hasattr(self.namespace, '__authentication__'):
			try:
				access_key = rvars.pop('_access_key')
			except KeyError:
				return self._build_response(errors=u'Please provide an access key')

			if (isinstance(self.namespace.__authentication__, str) or \
				isinstance(self.namespace.__authentication__, unicode)):
				if access_key <> self.namespace.__authentication__:
					return self._build_response(errors=u'Wrong access key')
			elif callable(self.namespace.__authentication__):
				if not self.namespace.__authentication__(access_key):
					return self._build_response(errors=u'Wrong access key')
			else:
				raise ValueError(u'__authentication__ can be either a callable or a string, not %s' % type(self.namespace.__authentication__))
		
		# check ipaddress restriction
		if hasattr(self.namespace, '__ip_restriction__'):
			if request.META.get('REMOTE_ADDR', 'n/a') not in self.namespace.__ip_restriction__:
				return self._build_response(errors=u'ip address not whitelisted')
		
		response_type = rvars.pop('_type', 'json')
		
		if response_type not in self.__response_types__.keys():
			return self._build_response(errors=u'Response type (%s) not found' % response_type)
		
		try:
			fname = rvars.pop('_call')
		except KeyError:
			return self._build_response(errors=u'_call not given')
		
		try:
			return self._build_response(
				self._handle_request(request, fname, rvars), response_type=response_type
			)
		except ResponseException, e:
			return self._build_response(
				response_type=response_type,
				errors=e
			)