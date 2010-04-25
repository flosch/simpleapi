# -*- coding: utf-8 -*-

import unittest

from simpleapi import *

class NamespaceTest(unittest.TestCase):

    def setUp(self):

        class TestNamespace(Namespace):
            pass

        self.namespace = TestNamespace()

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()