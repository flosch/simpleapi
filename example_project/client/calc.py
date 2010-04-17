# -*- coding: utf-8 -*-

import sys
sys.path.append("/Users/flosch/devlibs/3rdparty/")

from simpleapi import Client

calculator = Client(ns='http://localhost:8888/calculator/', access_key="91d9f7763572c7ebcce49b183454aeb0")
print "5 + 5 =", calculator.add(a=5, b=5)
print "5 * 5 =", calculator.multiply(a=5, b=5)
print "5 ** 5 =", calculator.power(a=5, b=5)