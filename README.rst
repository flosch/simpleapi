=========
simpleapi
=========

:version: 0.0.6-pre (alpha-stage)
:author: Florian Schlachter (http://www.fs-tools.de)
:license: MIT-license / see LICENSE file for more
:website: http://simpleapi.de
:mailinglist: subscribe: simpleapi@librelist.com

An almost complete documentation is still work in progress and will be published at http://www.simpleapi.de soon.

About
=====

simpleapi is an **easy to use, consistent, transparent and portable** way of providing an API within your django project. It supports **several output formats** (e. g. json, jsonp, xml) and provides a **client library** to access the API seamlessly from any python application. You can also use nearly every **Ajax framework** (e. g. jQuery, ExtJS, etc.) to access the API.

* dynamic key authentication / ip restriction
* type-conversion / constraints
* object serialization of django model instances, django queryset instances, 
  mongoengine documents, mongoengine queryset instances
* inheritance / multiple versions of one API
* several encoding/decoding formats (json, jsonp, xml, etc.)
* several result formats (ie. for ExtJS forms, etc.)
* features: caching, throttling
* examples

Installation
============

::
    
    pip install --upgrade django-simpleapi

From GitHub
-----------

::
    
    git clone git://github.com/flosch/simpleapi.git

Dependencies
============

* Python 2.5 or greater
* simplejson (if you're using Python <= 2.5)
* python-dateutil

(see requirements.txt as well)

Screencasts
===========

You should watch the screencasts in full screen.

:Contact-app: http://vimeo.com/11280195 (good quality: http://bit.ly/cUdogY)

Examples
========

SMS-System
----------

Server (handler.py)::

    from simpleapi import Namespace, serialize
    from models import SMS, APIUser
    
    class SMSAPI(Namespace):
        __authentication__ = lambda namespace, access_key: \
            APIUser.objects.filter(access_key=access_key).count() > 0

        def send(self, to, msg, from='testsender'):
            sms = SMS.objects.create(
                to=to
                msg=msg,
                from=from
            )
            return {
                'sent': sms.send(),
                'obj': serialize(sms, excludes=[re.compile('^date'),])
            }
        send.published = True
        send.constraints = {'to': re.compile(r'^\+\d{2,}\ \d{3,}\ \d{5,}')}
        
        def status(self, id):
            return SMS.objects.get(id=id)
        status.published = True
        status.constraints = {'id': int}
        
        def last(self, numbers=5):
            return SMS.objects.all()[:numbers]
        last.published = True
        last.constraints = {'numbers': int}

Server (urls.py)::

    from handlers import SMSAPI
    urlpatterns = patterns('',
        (r'^api/$', Route(SMSAPI))
    )

Client (python)::

    from simpleapi import Client
    
    client = Client(ns='http://remote.tld:8888/api/', access_key='mysecret',
                    transport_type='xml')
    
    sms = client.sms(to='555123', msg='Hey yo! This is simpleapi calling.')
    print "Sent successful?", sms['sent']
    
    sms = client.sms(to='555123', msg='2nd test with own sender',
                     sender='simpleapi')
    print "Sent successful?", sms['sent']
    print "Which sender?", sms['obj']['sender']

Client (jQuery)::

    jQuery.get(
        "/api/",
        {_call: 'send', to: '555123', 'msg': 'Hey ya!'},
        function (return) {
            if (return.result.sent)
                alert('Sent successfully!');
            else
                alert('Sending failed!');
        }
    )

Calculator
----------

Server (handler.py)::

    from simpleapi import Namespace
    
    class CalculatorAPI(Namespace):
        __ip_restriction__ = ['127.0.0.*',]
        __authentication = "lets_calc"
        
        def power(self, a, b):
            return a ** b
        power.published = True
        power.constraints = lambda namespace, key, value: float(value)
        
        def sum(self, **kwargs)
            return sum(kwargs.values())
        sum.published = True
        sum.constraints = lambda namespace, key, value: float(value)

Server (urls.py)::

    from handlers import CalculatorAPI
    urlpatterns = patterns('',
        (r'^api/$', Route(CalculatorAPI))
    )

Client (python)::

    from simpleapi import Client
    
    client = Client(ns='http://remote.tld:8888/api/', access_key='lets_calc')
    
    print "5 ** 8 =", client.power(a=5, b=8)
    print "1+2+3+4+5+6+7 =", client.sum(a=1, b=2, c=3, d=4, e=5, f=6, g=7)

Client (jQuery)::

    jQuery.get(
        "/api/",
        {_call: 'power', a: 5, b: 8, _access_key: "lets_calc"},
        function (return) {
            alert('5 ** 8 = ' + return.result)
        }
    )