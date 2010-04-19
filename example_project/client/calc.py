# -*- coding: utf-8 -*-

import sys
sys.path.append("/Users/flosch/devlibs/3rdparty/")

from simpleapi import Client, RemoteException

calculator = Client(ns='http://localhost:8888/api/calculator/multiple/', access_key="91d9f7763572c7ebcce49b183454aeb0")
print "(v2) 5 + 5 =", calculator.add(a=5, b=5)

# change api version to 1
calculator.set_version(1)
print "(v1) 5 + 5 =", calculator.add(a=5, b=5)

print "5 * 5 =", calculator.multiply(a=5, b=5)

# change namespace from multiple versions to Route with only one version
calculator.set_ns('http://localhost:8888/api/calculator/one/')
print "5 ** 5 =", calculator.power(a=5, b=5)

some_functions = Client(ns='http://localhost:8888/api/functions/', use_pickle=True)

# works only with simpleapi's python client because it's using cPickle functionality. JSON doesn't support to serialize date objects
print "Today's datetime:", some_functions.today()

print "Add a day, remotely by passing a datetime object to the function:", some_functions.add_a_day(dt=some_functions.today())

print "Finally, this method call fails:", 
try:
	some_functions.fail()
except RemoteException, e:
	print unicode(e)