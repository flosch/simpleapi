# -*- coding: utf-8 -*-

import copy
import unittest
try:
    import json
except ImportError:
    import simplejson as json
import cPickle

from simpleapi import *

class RouteTest(unittest.TestCase):
    
    _value_simple = 5592.61
    
    # in JSON key values of dict items must be of type string
    _value_complex = {
        'test1': u'test äöüß',
        'test2': 592,
        'test3': 1895.29596,
        'test4': {
            'sub': 'yes',
            'list': ['1', 2, 3.4, [5, 6], {'7': '8', '9': 10}]
        },
        '5': [6, 7, '8', '9', 10.11],
        '6': True,
        'test7': False,
        'test8': [True, 0, False, 1],
        u'täst9': 9
    } 

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
        
    def call(self, route, method, **kwargs):
        """Simulates a call to the API."""
        
        class Request(object):
            pass
        
        request = Request()
        request.REQUEST = {}
        request.META = {
            'REMOTE_ADDR': '127.0.0.1'
        }
        
        # set simpleapi parameters
        request.REQUEST['_call'] = method
        
        # make sure every transporttype returns the same result after
        # decoding the response content
        transporttypes = ['json', ]
        first_response = None
        for transporttype in transporttypes:
            # encode query parameters
            local_kwargs = copy.deepcopy(kwargs)
            for key, value in local_kwargs.iteritems():
                if transporttype == 'json':
                    local_kwargs[key] = json.dumps(value)
            
            request.REQUEST.update(local_kwargs)
            
            # set encoding/decoding parameters
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
        # test whether the published-flag works fine
        success, errors, result = self.call(self.route1, 'non_published')
        self.failIf(success)
        
        success, errors, result = self.call(self.route1, 'return_value', 
            val=self._value_complex)
        self.failUnless(success)
        self.failUnlessEqual(result, self._value_complex)
    
    def test_global_options(self):
        pass
    
    def test_namespace_versions(self):
        pass
        
    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()