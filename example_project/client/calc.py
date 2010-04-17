# -*- coding: utf-8 -*-

import sys
sys.path.append("/Users/flosch/devlibs/3rdparty/")

from simpleapi import Client

calculator = Client(ns='http://localhost:8888/calculator/')
print "5 + 5 =", calculator.add(a=5, b=5)
print "5 * 5 =", calculator.multiply(a=5, b=5)
print "5 ** 5 =", calculator.power(a=5, b=5)