# -*- coding: utf-8 -*-

from simpleapi import Namespace

class Calculator(Namespace):
	
	__ip_restriction__ = ["127.0.0.*", "78.47.135.*"]
	__authentication__ = "91d9f7763572c7ebcce49b183454aeb0"
	
	def multiply(self, a, b):
		return a*b	
	multiply.published = True
	multiply.types = {'a': float, 'b': float}
	
	def power(self, a, b):
		return a**b	
	power.published = True
	power.types = {'a': float, 'b': float}
	
class OldCalculator(Calculator):
	
	__version__ = 1
	
	def add(self, a, b):
		return a+b
	add.published = True
	add.types = {'a': float, 'b': float}

class NewCalculator(Calculator):
	
	__version__ = 2
	
	def add(self, a, b):
		return a+b+1
	add.published = True
	add.types = {'a': float, 'b': float}

class SomeFunctions(Namespace):
	
	__features__ = ['pickle', 'caching']
	__input__ = ['pickle'] # restrict input to pickle only (since we're using datetime objects as input and use only the simpleapi client)
	__output__ = ['pickle'] # restrict output to pickle only
	
	def today(self):
		import datetime
		return datetime.datetime.now()
	today.published = True

	def fail(self):
		self.error('This fails remotely!')
	fail.published = True
	
	def add_a_day(self, dt):
		import datetime
		return dt+datetime.timedelta(days=1)
	add_a_day.published = True

	def delayed_function(self, a, b, c=95):
		import time
		time.sleep(3)
		return True
	delayed_function.published = True
	delayed_function.caching = {
		'timeout': 15, # in seconds
	} # Caching is available because 'caching' is added to the list of __features__ (see above)!