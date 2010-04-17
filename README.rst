=========
simpleapi
=========

:stage: unstable
:author: Florian Schlachter (http://www.fs-tools.de)
:license: see LICENSE file for more (simpleapi is licensed under MIT license)

About
=====

simpleapi is an easy to use, consistent and portable way of providing an API within your django project. It supports several output formats (e. g. json, xml) and provides a client library to access the API seamlessly from any python application.

The server supports:

* API-namespaces to bundle methods
* dynamic key authentication / ip restriction
* type-conversion
* inheritance (create abstract namespaces and use them as superclasses)
* support for multiple API versions

The client supports:

* super simple access to server functions
* easy to switch between different api versions

Server example
==============

First example
-------------

handlers.py::

    from simpleapi import Namespace
    
    class JobNamespace(Namespace):
        __ip_restriction__ = ["127.0.0.*", "78.47.135.*"] # only allow specific ip-addresses
        __authentication__ = "91d9f7763572c7ebcce49b183454aeb0" # you can either use a callable here (for dynamic authentication) or provide a static key for authentication
    
        def status(self, job_id):
            # get the job by job_id ...
            return job.get_status()
        status.published = True # make the method available via API

    class SMSNamespace(JobNamespace):
        def new(self, to, msg, sender='my website', priority=5):
            # send sms ...
        status.published = True # make the method available via API
        status.methods = ('POST', ) # limit access to POST
        status.types = {'priority': int} # ensure that priority argument is of type int

urls.py::

    from simpleapi import Route
    from handlers import SMSNamespace, FaxNamespace

    urlpatterns = patterns('',
    	(r'^job/sms/$', Route(SMSNamespace)),
    	(r'^job/fax/$', Route(FaxNamespace)),
    )

Second example with multiple API versions
-----------------------------------------

handlers.py::


urls.py::


HTTP call and parameters
------------------------

Clients are able to call the procedures like::

    http://www.yourdomain.tld/job/sms/?_call=new&to=012345364&msg=Hello!&sender=from+me
    http://www.yourdomain.tld/job/sms/?_call=status&_type=xml&job_id=12345678

The following parameters are used by simpleapi:

:_call: method to be called
:_type: output format (e. g. xml, json; default is json)
:_version: version number of the API that should be used
:_access_key: access key to the API (only if `__authentiation__` in `namespace` is defined)

Client example
==============

This is how you can access your published methods within any python application::

    from simpleapi import Client

    SMS = Client(ns='http://yourdomain.tld/api/job/sms/')
    new_sms = SMS.new(
    	phonenumber="+49 123 456789",
    	message="Short test"
    )

new_sms contains the returned function value.

How to run the demo
===================

1. Start the server with `./manage.py runserver 127.0.0.1:8888`
2. Start the client `python calc.py`

(Make sure simpleapi is in your PATH)

Tips & tricks
=============

# Make sure to remove or deactivate the new csrf-middleware functionality of django 1.2 for the Route.
# Use SSL to encrypt the datastream.
# Use key authentication, limit ipaddress access to your business' network.

TODO
====

# method-based verification
# usage limitations (#/second, #/hour, etc.) per user