# -*- coding: utf-8 -*-

import unittest
try:
    import json
except ImportError:
    import simplejson as json
import cPickle

from simpleapi import *

class RouteTest(unittest.TestCase):

    def setUp(self):
        
        class TestNamespace(Namespace):
            
            def return_value(self, val):
                return val
            return_value.published = True
            
            def non_published(self):
                return True
        
        class TestNamespace1(TestNamespace):
            __version__ = 1

        class TestNamespace2(TestNamespace):
            __version__ = 2
                
        self.route1 = Route(TestNamespace)
        self.route2 = Route(TestNamespace1, TestNamespace2)
        
    def call(self, route, method, data={}):
        class Request(object):
            def __init__(self):
                pass
        
        data['_call'] = method
        
        request = Request()
        request.REQUEST = data
        request.META = {
            'REMOTE_ADDR': '127.0.0.1'
        }
        
        # make sure every transporttype returns the same result after
        # decoding the response content
        transporttypes = ['json', ]
        first_response = None
        for transporttype in transporttypes:
            request.REQUEST['_input'] = transporttype
            request.REQUEST['_output'] = transporttype
            http_response = route(request)
            
            if transporttype == 'json':
                response = json.loads(http_response.content)
            else:
                self.fail(u'unknown transport type: %s' % transporttype)
            
            if not first_response:
                first_response = response
            else:
                self.failUnlessEqual(response, first_response)
        
        return (
            response.get('success'),
            response.get('errors'),
            response.get('result')
        )
    
    def test_local_options(self):
        success, errors, result = self.call(self.route1, 'non_published')
        self.failIf(success)
    
    def test_global_options(self):
        pass
    
    def test_namespace_versions(self):
        pass
        
    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()