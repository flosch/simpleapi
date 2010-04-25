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
            
            __features__ = ['pickle',]
            
            def return_value(self, val):
                return val
            return_value.published = True
            
            def non_published(self):
                return True
            
            def power(self, a, b):
                return a ** b
            power.published = True
            
            def sum_up(self, **kwargs):
                return sum(kwargs.values())
            sum_up.constraints = lambda key, value: int(value)
            
            def get_version(self):
                return self.__version__
            get_version.published = True
        
        class TestNamespace1(TestNamespace):
            __version__ = 1
        
        class TestNamespace2(TestNamespace):
            __version__ = 2
            __authentication__ = "abc"
        
        class TestNamespace3(TestNamespace):
            __version__ = 3
            __authentication__ = lambda namespace, access_key: access_key == 'a' * 5
        
        class TestNamespace4(TestNamespace):
            __version__ = 4
                
        self.route1 = Route(TestNamespace)
        self.route2 = Route(
            TestNamespace1,
            TestNamespace2,
            TestNamespace3,
            TestNamespace4
        )
        
    def call(self, route, method, version='default', access_key=None, 
             transporttypes=None, **kwargs):
        """Simulates a call to the API."""
        
        class Request(object):
            pass
        
        request = Request()
        request.method = 'POST'
        request.REQUEST = {}
        request.META = {
            'REMOTE_ADDR': '127.0.0.1'
        }
        
        # set simpleapi parameters
        request.REQUEST['_call'] = method
        request.REQUEST['_version'] = version
        if access_key:
            request.REQUEST['_access_key'] = access_key
        
        # make sure every transporttype returns the same result after
        # decoding the response content
        transporttypes = transporttypes or ['json', 'pickle']
        first_response = None
        for transporttype in transporttypes:
            # encode query parameters
            local_kwargs = copy.deepcopy(kwargs)
            for key, value in local_kwargs.iteritems():
                if transporttype == 'json':
                    local_kwargs[key] = json.dumps(value)
                elif transporttype == 'pickle':
                    local_kwargs[key] = cPickle.dumps(value)
            
            request.REQUEST.update(local_kwargs)
            
            # set encoding/decoding parameters
            request.REQUEST['_input'] = transporttype
            request.REQUEST['_output'] = transporttype
            
            # fire it up!
            http_response = route(request)
            if transporttype == 'json':
                response = json.loads(http_response.content)
            elif transporttype == 'pickle':
                response = cPickle.loads(http_response.content)
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
    
    def test_published(self):
        # test: published-flag
        success, errors, result = self.call(self.route1, 'non_published')
        self.failIf(success)
        
        success, errors, result = self.call(self.route1, 'return_value', 
            val=self._value_complex)
        self.failUnless(success)
        self.failUnlessEqual(result, self._value_complex)
    
    def test_data(self):
        # test: _data
        success, errors, result = self.call(self.route1, 'power', _data={'a': 3, 'b': 10})
        self.failUnlessEqual(result, 59049)
    
    def test_authentication(self):
        # test: __authentication__
        
        # __authentication__ == "abc"
        success, errors, result = self.call(
            route=self.route2,
            method='power',
            version='2'
        )
        self.failIf(success)
        self.failUnless(u'Authentication failed.' == errors[0])
        
        success, errors, result = self.call(
            route=self.route2,
            method='power',
            version='2',
            access_key='abc',
            a=1,
            b=2
        )
        self.failUnless(success)
        
        # __authentication__ == lambda namespace, access_key: access_key == 'a' * 5
        success, errors, result = self.call(
            route=self.route2,
            method='power',
            version='3'
        )
        self.failIf(success)
        self.failUnless(u'Authentication failed.' == errors[0])
        
        success, errors, result = self.call(
            route=self.route2,
            method='power',
            version='3',
            access_key='a' * 5,
            a=1,
            b=2
        )
        self.failUnless(success)
    
    def test_kwargs(self):
        # test: kwargs
        success, errors, result = self.call(
            route=self.route1,
            method='power',
            version='3'
        )
        # TODO
    
    def test_constraints(self):
        pass
    
    def test_versions(self):
        # test: __version__ 
        success, errors, result = self.call(
            route=self.route1,
            method='power',
            version='3'
        )
        self.failIf(success)
        self.failUnless(u'Version 3 not found' in errors[0])
        
        success, errors, result = self.call(
            route=self.route2,
            method='get_version',
            version='1'
        )
        self.failUnless(success)
        self.failUnlessEqual(result, 1)
        
        success, errors, result = self.call(
            route=self.route2,
            method='get_version',
            version='4'
        )
        self.failUnless(success)
        self.failUnlessEqual(result, 4)
        
        success, errors, result = self.call(
            route=self.route2,
            method='get_version',
            version='default'
        )
        self.failUnless(success)
        self.failUnlessEqual(result, 4)
        
        # add new namespace with same version
        class TestNamespace(Namespace):
            __version__ = 4
        self.failUnlessRaises(AssertionError, lambda: self.route2.add_namespace(TestNamespace))
        
        # add new namespace with new version
        class TestNamespace(Namespace):
            __version__ = 999
            def get_version(self):
                return self.__version__
            get_version.published = True
            
        self.failUnlessEqual(self.route2.add_namespace(TestNamespace), 999)
        
        success, errors, result = self.call(
            route=self.route2,
            method='get_version',
            version='default',
            transporttypes=['json',]
        )
        self.failUnless(success)
        self.failUnlessEqual(result, 999)
        
        # remove added namespace again
        self.failUnless(self.route2.remove_namespace(999))
        self.failIf(self.route2.remove_namespace(999))
        
        success, errors, result = self.call(
            route=self.route2,
            method='get_version',
            version='default'
        )
        self.failUnless(success)
        self.failUnlessEqual(result, 4)
    
    def test_pickle(self):
        # test: pickle
        # UnpicklingError
        
        class Test(Namespace):
            def return_val(self, val):
                return val
            return_val.published = True
        self.route3 = Route(Test)
        self.failUnlessRaises(
            cPickle.UnpicklingError,
            lambda: self.call(route=self.route3, method='return_val')
        )
        del self.route3
    
    def test_global_options(self):
        pass
    
    def test_namespace_versions(self):
        pass
        
    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()