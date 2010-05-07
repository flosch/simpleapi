# -*- coding: utf-8 -*-

import re
import copy
import unittest
try:
    import json
except ImportError:
    import simplejson as json
import cPickle

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'

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

            __input__ = ['pickle', 'json',]
            __output__ = ['pickle', 'json',]

            def return_value(self, val):
                return val
            return_value.published = True

            def non_published(self):
                return True

            def power(self, a, b):
                return a ** b
            power.published = True
            power.constraints = {'a': lambda value: float(value), 'b': int}

            def sum_up(self, a, d=0, **kwargs):
                return a + sum(kwargs.values()) - d
            sum_up.published = True
            sum_up.constraints = lambda namespace, key, value: int(value)

            def get_version(self):
                return self.__version__
            get_version.published = True

            def call_phone(self, phone_number):
                return True
            call_phone.published = True
            call_phone.constraints = {
                'phone_number': re.compile(r"^\+\d{1,} \d{2,} \d{2,}$"),
            }

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
        transporttypes = transporttypes or ['json', 'pickle',]
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
        self.failUnlessEqual(u'Authentication failed.', errors[0])

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
        self.failUnlessEqual(u'Authentication failed.', errors[0])

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
            method='sum_up',
            a=5,
            b=7,
            c=99,
            e=100
        )
        self.failUnless(success)
        self.failUnlessEqual(result, 211)

        success, errors, result = self.call(
            route=self.route1,
            method='power',
            a=5,
            b=7,
            c=99
        )
        self.failIf(success)
        self.failUnlessEqual(u'Unused arguments: c', errors[0])

    def test_default_args(self):
        success, errors, result = self.call(
            route=self.route1,
            method='sum_up',
            a='5',
            d=5,
            c='99',
            e='100'
        )
        self.failUnless(success)
        self.failUnlessEqual(result, 199)

    def test_constraints(self):
        # test: constraints[phone_number] = regular expression
        success, errors, result = self.call(
            route=self.route1,
            method='call_phone',
            phone_number='0176123456'
        )
        self.failIf(success)
        self.failUnlessEqual(u'Constraint failed for argument: phone_number', errors[0])

        success, errors, result = self.call(
            route=self.route1,
            method='call_phone',
            phone_number='+49 176 123456'
        )
        self.failUnless(success)
        self.failUnlessEqual(result, True)

        # test: constraints = lambda namespace, key, value: int(value)
        success, errors, result = self.call(
            route=self.route1,
            method='sum_up',
            a='afs',
            d=5,
            c=99,
            e=100
        )
        self.failIf(success)
        self.failUnlessEqual(u'Constraint failed for argument: a', errors[0])

        # test: type conversion
        success, errors, result = self.call(
            route=self.route1,
            method='sum_up',
            a='19',
            d='5',
            c='99',
            e='1020'
        )
        self.failUnless(success)
        self.failUnlessEqual(result, 1133)

        # test: constraints[a] = lambda value: float(value), b = int
        success, errors, result = self.call(
            route=self.route1,
            method='power',
            a='19.95',
            b='4'
        )
        self.failUnless(success)
        self.failUnlessEqual(result, 158405.99000624998)

        success, errors, result = self.call(
            route=self.route1,
            method='power',
            a='19.95',
            b='4.5'
        )
        self.failIf(success)
        self.failUnlessEqual(u'Constraint failed for argument: b', errors[0])


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

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()