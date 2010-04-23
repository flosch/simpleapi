# -*- coding: utf-8 -*-

import re
from simpleapi import Namespace

class Calculator(Namespace):
	
	__ip_restriction__ = ["127.0.0.*", "78.47.135.*"]
	__authentication__ = lambda self, access_key: access_key == "91d9f7763572c7ebcce49b183454aeb0"
	
	def get_access_keys(self):
		return (self.__authentication__, self.session.access_key)
	get_access_keys.published = True
	
	def multiply(self, a, b):
		return a*b	
	multiply.published = True
	multiply.constraints = {'a': float, 'b': float}
	
	def power(self, a, b):
		return a**b	
	power.published = True
	power.constraints = {'a': float, 'b': lambda b: float(b)}
	
	def verify_sum_up(self, key, value):
		return float(value) # verifiies also all kwargs!
	
	def sum_up(self, **kwargs):
		return sum(kwargs.values())
	sum_up.published = True
	sum_up.constraints = verify_sum_up
	
	def verifiy_get_max(self, key, value):
		return float(value)
	verifiy_get_max.name = 'float'
	
	def get_max(self, a, b):
		return max(a, b)
	get_max.published = True
	get_max.constraints = {'a': verifiy_get_max, 'b': verifiy_get_max}
	
class OldCalculator(Calculator):
	
	__authentication__ = "91d9f7763572c7ebcce49b183454aeb0"
	
	__version__ = 1
	
	def add(self, a, b):
		return a+b
	add.published = True
	add.constraints = {'a': float, 'b': float}

class NewCalculator(Calculator):
	
	__version__ = 2
	
	def add(self, a, b):
		return a+b+1
	add.published = True
	add.constraints = {'a': float, 'b': float}

class SomeFunctions(Namespace):
	
	__features__ = ['pickle', 'caching']
	__input__ = ['pickle'] # restrict input to pickle only (since we're using datetime objects as input and use only the simpleapi client)
	__output__ = ['pickle'] # restrict output to pickle only
	
	def regex_constraint(self, value):
		return True
	regex_constraint.published = True
	regex_constraint.constraints = {'value': re.compile(r'^\d{5}\-\w{3,7}$')}
	
	def get_remote_ip(self):
		return self.session.request.META.get('REMOTE_ADDR')
	get_remote_ip.published = True
	
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

class Misc(Namespace):
    
    def return_my_value(self, val):
        return val
    return_my_value.published = True