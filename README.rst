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
* several output formats (json, jsonp, xml, etc.)

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
        new.published = True # make the method available via API
        new.methods = ('POST', ) # limit access to POST
        new.types = {'priority': int} # ensure that priority argument is of type int

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

    from simpleapi import Namespace
    
    class JobNamespace(Namespace):
        __ip_restriction__ = ["127.0.0.*", "78.47.135.*"] # you can either use a callable here or provide a list of ip addresses
        __authentication__ = "91d9f7763572c7ebcce49b183454aeb0" # you can either use a callable here (for dynamic authentication) or provide a static key for authentication
        
        def _get_job_by_id(self, job_id):
            # get the job by job_id
            # this method isn't published to the public and isn't 
            # made accessable via API since it's missing the published-flag
            return Job.objects.get(id=job_id)
    
        def status(self, job_id):
            job = self._get_job_by_id(job_id)
            return job.get_status()
        status.published = True # make the method available via API
        status.types = {'job_id': str}

    class OldSMSNamespace(JobNamespace):
        __version__ = 1
    
        def new(self, to, msg):
            # send sms ...
        new.published = True # make the method available via API
    
    class NewSMSNamespace(JobNamespace):
        __version__ = 2

        def new(self, phonenumber, message, sender='my website', priority=5):
            # send sms ...
        new.published = True # make the method available via API
        new.methods = ('POST', ) # limit access to POST
        new.types = {'priority': int} # ensure that priority argument is of type int

urls.py::

    from simpleapi import Route
    from handlers import OldSMSNamespace, NewSMSNamespace, FaxNamespace

    urlpatterns = patterns('',
        (r'^job/fax/$', Route(FaxNamespace)), # Route with exact one namespace
        (r'^job/sms/$', Route(OldSMSNamespace, NewSMSNamespace)), # Route can hold different versions of namespaces
    )

The namespace with the highest version is the default one which will be used when the client doesn't provide a version.

Third example (which is restricted in use to the simpleapi client)
------------------------------------------------------------------

handlers.py::

    import datetime
    from simpleapi import Namespace
    
    class SomeFunctions(Namespace):
        def today(self):
            return datetime.datetime.now()
        today.published = True
        today.outputs = ['pickle',] # limit output format to pickle (which currently supports the simpleapi client only)

urls.py as above. You can call the method with the simpleapi client as usual, but calling the method for instance via Ajax won't work.

Client example with simpleapi's client library
==============================================

This is how you can access your published methods from any python application::

First example
-------------

::

    from simpleapi import Client

    SMS = Client(ns='http://yourdomain.tld/api/job/sms/')
    new_sms = SMS.new(
    	to="+49 123 456789",
    	msg="Short test"
    )

Second example (with version change)
------------------------------------

::

    from simpleapi import Client

    SMS = Client(ns='http://yourdomain.tld/api/job/sms/', version=2)
    new_sms = SMS.new(
    	phonenumber="+49 123 456789",
    	message="Short test"
    )
    
    SMS.set_version(1) # back to the old API-version (which takes differently named arguments)
    
    new_sms = SMS.new(
	    to="+49 123 456789",
	    msg="Short test"    
    )

Configuration and development
=============================

Namespace's methods
-------------------

In order to make a method available and callable from outside (the client party) and to configure the called method simpleapi reads some configuration variables for each method. They are configured as follows::

    class MyNamespace(Namespace):
        def my_api_method(self, arg1):
            return arg1
        my_api_method.configuration_var = value

The following configuration parameters are existing:

:published: make the method available and callable from outside (boolean)
:types: a dict where you can specify a type of which one parameter must be of. The parameter will be converted into your desired type (if simpleapi cannot, it wil raise an error to the client). See the examples for more.
:methods: specifies which HTTP methods are allowed to call the method (a list; by default it allows every method). If you plan to receive a huge amount of data (like a file), you should only allow POST as this can manage "unlimited" data (GET is limited to 1024 bytes which is fairly enough for much function calls though).
:outputs: if specified, the output formatters are limited for this method (a list; e. g. useful, if you plan to return values that cannot be serialized by the json-module but can be pickled and compatibility to Ajax and others isn't an issue for you)

HTTP call and parameters
------------------------

Clients are able to call the procedures like::

    http://www.yourdomain.tld/job/sms/?_call=new&to=012345364&msg=Hello!&sender=from+me
    http://www.yourdomain.tld/job/sms/?_call=status&_output=xml&job_id=12345678

The following parameters are used by simpleapi:

:_call: method to be called
:_output: output format (e. g. xml, json; default is json)
:_version: version number of the API that should be used
:_access_key: access key to the API (only if `__authentiation__` in `namespace` is defined)
:_callback: defines the callback for JSONP (default is `simpleapiCallback`)
:_mimetype: `simpleapi` automatically sets the correct mime type depending on the output format. you can set a different mimetype by set this http parameter.

Usage in Web-Apps
-----------------

Imagine the following server implementation which will be used for the web-apps examples:

    from simpleapi import Namespace
    
    class Calculator(Namespace):
    	def multiply(self, a, b):
    		return a*b	
    	multiply.published = True
    	multiply.types = {'a': float, 'b': float}

    	def power(self, a, b):
    		return a**b	
    	power.published = True
    	power.types = {'a': float, 'b': float}

The next two chapters are covering Ajax (with jQuery) and crossdomain-Requests.

Usage in web-apps (Ajax+jQuery)
-------------------------------

If your functions are not limited to an specific output formatter (which is the default) you're able to call the functions (within the same domain) via Ajax (XMLHttpRequest). I prefer using jQuery or ExtJS which makes calling remote functions a snap. The following example is using jQuery::

    jQuery.get("/myapi/", {_call: 'multiply', a: 5, b: 10}, function (result) {
        alert('A * 10 = ' + result);
    })

For more informaton on jQuery's ajax capabilities see here: http://api.jquery.com/category/ajax/

See the demo project for an example implementation.

Usage in web-apps (crossdomain)
-------------------------------

If you want to call a API method from a third-party page (which isn't located on the same domain as the server API) you cannot use XMLHttpRequest due to browser security restrictions. 

In this case you can use simpleapi's JSONP implementation which allows you to call functions and get the result via a callback. Some Ajax implementations (like jQuery and ExtJS) support transparent Ajax requests which internally uses the <script>-tag to get access to the remote function. In jQuery it looks like::

    $.ajax({
        url: "http://127.0.0.1:8888/api/calculator/one/",
        data: {_call: 'multiply', a: 5, b: 10},
        dataType: "jsonp",
        jsonp: "_callback", // needed since simpleapi names his callback-identifier "_callback"
        success: function (result) {
            alert('A * 10 = ' + result);
        }
    })

See the demo project for an example implementation.

Supported output formats
------------------------

* JSON ("json")
* JSONP ("jsonp")
* cPickle (used by the simpleapi client) ("pickle")
* XML (coming) ("xml")


How to run the demo
===================

1. Start the server with `./manage.py runserver 127.0.0.1:8888`
2. Start the client `python calc.py`

(Make sure simpleapi is in your PATH)

Tips & tricks
=============

0. Take a look on my example project (example_project/[client|server]) for a first view on how simpleapi works.
1. Make sure to remove or deactivate the new csrf-middleware functionality of django 1.2 for the Route.
2. Use SSL to encrypt the datastream.
3. Use key authentication, limit ip-address access to your business' network or server.
4. You can set up a simple throtteling by setting a callable to `__ip_restriction__` which keeps track at every request of an ip-address (the callable gets the ip-address of the calling party as the first argument). 
5. You can outsource your namespace's settings by creating new vars in your local settings.py file (e. g. `NAMESPACE_XY_IP_RESTRICTIONS=["127.0.0.*", ]`) and reference them within your namespace (like `__ip_restriction__ = settings.NAMESPACE_XY_IP_RESTRICTIONS`)

Limitations
===========

1. Only if you're not simpleapi's python client (which uses cPickle for serializing the data): The output/return value of a method is limited to the formatter's restrictions. For instance, you cannot return datetime values since they aren't supported by JSON (use datetime.isotime() instead). 

TODO
====

1. method-based verification
2. usage limitations (#/second, #/hour, etc.) per user
3. cache return value when the arguments of one request are exactly the same