# -*- coding: utf-8 -*-

import sys
sys.path.append("../../../../")

from simpleapi.client import Client, RemoteException

calculator = Client(ns='http://localhost:5000/api/',
                    transport_type='xml', timeout=60)

print "5 + 5 =", calculator.add(a=5, b=16)