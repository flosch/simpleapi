# -*- coding: utf-8 -*-

__all__ = ('Namespace', 'Route')

import json
import inspect
import cPickle

from django.conf import settings
from django.http import HttpResponse

from utils import glob_list

class NamespaceException(Exception): pass
class Namespace(object):
	
	def error(self, err_or_list):
		raise ResponseException(err_or_list)

class JSONResponse(object):
	
	__mime__ = "application/json"
	
	def build(self, data, callback):
		return json.dumps(data)

class JSONPResponse(object):
	
	__mime__ = "application/javascript"

	def build(self, data, callback):
		return u'%s(%s)' % (callback or 'simpleapiCallback', json.dumps(data))

class XMLResponse(object):
	
	__mime__ = "text/xml"
	
	def build(self, data, callback):
		raise NotImplemented

class PickleResponse(object):
	
	__mime__ = "application/octet-stream"
	
	def build(self, data, callback):
		return cPickle.dumps(data)

class RouteException(Exception): pass
class ResponseException(RouteException): pass

class Route(object):
	
	__response_types__ = {
		'json': JSONResponse(),
		'jsonp': JSONPResponse(),
		'xml': XMLResponse(),
		'pickle': PickleResponse()
	}
	
	def __init__(self, *namespaces):
		self.namespace_map = {}
		
		for namespace in namespaces:
			version = getattr(namespace, '__version__', 'default')
			
			if self.namespace_map.has_key(version):
				raise ValueError(u'Duplicate API version')
			
			functions = filter(lambda fn: '__' not in fn[0], dict(inspect.getmembers(namespace)).items())
			functions = filter(lambda fn: getattr(fn[1], 'published', False) is True, functions)
			functions = map(lambda item: (item[0], {'fn': item[1], 'vars': inspect.getargspec(item[1])}), functions)
			functions = dict(functions)
			
			self.namespace_map[version] = {'instance': namespace(), 'functions': functions}
		
			# make glob list from ip address ranges
			if hasattr(namespace, '__ip_restriction__'):
				self.namespace_map[version]['instance'].__ip_restriction__ = glob_list(namespace.__ip_restriction__)
		
		# create default namespace (= latest version)
		self.namespace_map['default'] = self.namespace_map[max(self.namespace_map.keys())]
	
	def _build_response(self, data=None, response_type='json', errors=None, success=None, callback=None, mimetype=None):
		result = {}
		
		if errors is not None:
			result['errors'] = isinstance(errors, list) and errors or [unicode(errors),]
		
		if success is None:
			success = errors is None
		result['success'] = success
		
		if data is not None:
			result['result'] = data
		
		resp_type_inst = self.__response_types__[response_type]
		
		return HttpResponse(
			resp_type_inst.build(result, callback),
			mimetype=mimetype or getattr(resp_type_inst, '__mime__', 'text/plain')
		)
	
	def _get_function(self, fname, version):
		namespace_item = self.namespace_map[version]
		namespace = namespace_item['instance']
		functions = namespace_item['functions']
		
		if fname not in functions.keys():
			raise ResponseException(u'Method (%s) not found' % fname)
		
		fitem = functions[fname]
		
		return (fitem, namespace)
	
	def _handle_request(self, request, rvars, fname, fitem, namespace):
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
			result = func(namespace, *args, **kwargs)
		except Exception, e:
			trace = inspect.trace()
			msgs = []
			msgs.append('')
			msgs.append(u"******* Exception raised *******")
			msgs.append(u"Function call: %s" % fname)
			msgs.append(u"Variables: %s, %s" % (args, kwargs))
			msgs.append(u'Exception type: %s' % type(e))
			msgs.append(u'Exception msg: %s' % e)
			msgs.append('')
			msgs.append(u'------- Traceback follows -------')
			for idx, item in enumerate(trace):
				msgs.append(u"(%s)\t%s:%s (%s)" % (idx+1, item[3], item[2], item[1]))
				for line in item[4]:
					msgs.append(u"\t\t%s" % line.strip())
				msgs.append('') # blank line
			msgs.append('     -- End of traceback --     ')
			msgs.append('')
			print "\n".join(msgs) # TODO send it to the admins by email!
			raise ResponseException(u'An internal error occurred during your request.')
		
		return result
	
	def __call__(self, request):
		rvars = dict(request.REQUEST.iteritems())
		
		# get mimetype
		mimetype = rvars.pop('_mimetype', None)
		
		# get _callback for jsonp
		callback = rvars.pop('_callback', '')
		
		# check version
		version = rvars.pop('_version', 'default')
		
		if version <> 'default':
			try:
				version = int(version)
			except ValueError:
				return self._build_response(errors=u'API-version must be an integer (available versions: %s)' % ", ".join(map(lambda x: str(x), self.namespace_map.keys())))
		
		
		if not self.namespace_map.has_key(version):
			return self._build_response(errors=u'API-version not found (available versions: %s)' % ", ".join(map(lambda x: str(x), self.namespace_map.keys())))
		
		# determine default namespace
		namespace = self.namespace_map[version]['instance']
		
		# check authentication
		access_key = rvars.pop('_access_key', None)
		if hasattr(namespace, '__authentication__'):
			if not access_key:
				return self._build_response(errors=u'Please provide an access key')
			
			if not namespace.__authentication__:
				raise ValueError(u'If you want use authentication, you must provide either a static key or a callable.')
			
			if (isinstance(namespace.__authentication__, str) or \
				isinstance(namespace.__authentication__, unicode)):
				if access_key <> namespace.__authentication__:
					return self._build_response(errors=u'Wrong access key')
			elif callable(namespace.__authentication__):
				if not namespace.__authentication__(access_key):
					return self._build_response(errors=u'Wrong access key')
			else:
				raise ValueError(u'__authentication__ can be either a callable or a string, not %s' % type(namespace.__authentication__))
		
		# check ipaddress restriction
		if hasattr(namespace, '__ip_restriction__'):
			if callable(namespace.__ip_restriction__):
				if not namespace.__ip_restriction__(request.META.get('REMOTE_ADDR')):
					return self._build_response(errors=u'permission denied')
			elif request.META.get('REMOTE_ADDR', 'n/a') not in namespace.__ip_restriction__:
				return self._build_response(errors=u'permission denied')
		
		response_type = rvars.pop('_output', 'json')
		
		if response_type not in self.__response_types__.keys():
			return self._build_response(errors=u'Response type (%s) not found' % response_type)
		
		try:
			fname = rvars.pop('_call')
		except KeyError:
			return self._build_response(errors=u'_call not given')
		
		try:
			fitem, namespace = self._get_function(fname, version)
			
			# check whether output configuration is set
			func = fitem['fn']
			
			if hasattr(func, 'outputs'):
				assert isinstance(func.outputs, list) or isinstance(func.outputs, tuple)
				if response_type not in func.outputs:
					return self._build_response(errors=u'Response type (%s) not allowed (allowed: %s)' % (response_type, ", ".join(func.outputs)))
			
			return self._build_response(
				self._handle_request(request, rvars, fname, fitem, namespace),
				response_type=response_type,
				callback=callback,
				mimetype=mimetype
			)
		except ResponseException, e:
			return self._build_response(
				response_type=response_type,
				errors=e
			)