# -*- coding: utf-8 -*-

from simpleapi import Namespace

class Calculator(Namespace):
	
	__ip_restriction__ = ["127.0.0.*", "78.47.135.*"]
	__authentication__ = "91d9f7763572c7ebcce49b183454aeb0"
	
	def add(self, a, b):
		return a+b
	add.published = True
	add.types = {'a': float, 'b': float}
	
	def multiply(self, a, b):
		return a*b	
	multiply.published = True
	multiply.types = {'a': float, 'b': float}
	
	def power(self, a, b):
		return a**b	
	power.published = True
	power.types = {'a': float, 'b': float}