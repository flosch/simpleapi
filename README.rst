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
* authentication to clients
* type-conversion
* inheritance (create abstract namespaces and use them as superclasses)

The client supports:

* TBD

Server example
==============

your handlers.py::

    from simpleapi import Namespace
    
    class JobNamespace(Namespace):
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

your urls.py::

    from simpleapi import Route
    from handlers import SMSNamespace, FaxNamespace

    urlpatterns = patterns('',
    	(r'^job/sms/$', Route(SMSNamespace)),
    	(r'^job/fax/$', Route(FaxNamespace)),
    )

Clients are able to call the procedures like::

    http://www.yourdomain.tld/job/sms/?_call=new&to=012345364&msg=Hello!&sender=from+me
    http://www.yourdomain.tld/job/sms/?_call=status&_type=xml&job_id=12345678
    
The argument `_call` defines the method to be called; `_type` defines which output format should be used (default is json).