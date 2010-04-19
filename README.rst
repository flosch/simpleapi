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
:_callback: defines the callback for JSONP (default is `simpleapiCallback`)
:_mimetype: `simpleapi` automatically sets the correct mime type depending on the output format. you can set a different mimetype by set this http parameter.

Supported output formats
------------------------

* JSON
* JSONP
* XML (coming)

Client example
==============

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

How to run the demo
===================

1. Start the server with `./manage.py runserver 127.0.0.1:8888`
2. Start the client `python calc.py`

(Make sure simpleapi is in your PATH)

Tips & tricks
=============

1. Make sure to remove or deactivate the new csrf-middleware functionality of django 1.2 for the Route.
2. Use SSL to encrypt the datastream.
3. Use key authentication, limit ip-address access to your business' network.
4. You can set up a simple throtteling by setting a callable to `__ip_restriction__` which keeps track at every request of an ip-address (the callable gets the ip-address of the calling party as the first argument). 

Limitations
===========

1. The output/return value of a method is limited to the formatter's restrictions. For instance, you cannot return datetime values since they aren't supported by JSON (use datetime.isotime() instead). 

TODO
====

1. method-based verification
2. usage limitations (#/second, #/hour, etc.) per user