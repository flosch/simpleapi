# -*- coding: utf-8 -*-

import unittest

from simpleapi import *

class RouteTest(unittest.TestCase):

    def setUp(self):
        
        class TestNamespace(Namespace):
            pass
        
        class TestNamespace1(Namespace):
            __version__ = 1

        class TestNamespace2(Namespace):
            __version__ = 2
                
        self.route1 = Route(TestNamespace)
        self.route2 = Route(TestNamespace1, TestNamespace2)
        
    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()