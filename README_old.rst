=========
simpleapi
=========

:version: 0.0.6-pre
:author: Florian Schlachter (http://www.fs-tools.de)
:license: see LICENSE file for more (simpleapi is licensed under MIT license)
:website: http://simpleapi.de
:mailinglist: subscribe: simpleapi@librelist.com

This readme is a short (and messy) overview about simpleapi. There is still an 
almost complete documentation work in progress which will be published on http://www.simpleapi.de soon.

About
=====

simpleapi is an **easy to use, consistent and portable** way of providing an API within your django project. It supports **several output formats** (e. g. json, jsonp, xml) and provides a **client library** to access the API seamlessly from any python application. You can also use nearly every **Ajax framework** (e. g. jQuery, ExtJS, etc.) to access the API (see more at "Usage in web-apps" in this README).

Server features:

* provides API-namespaces to bundle methods
* has dynamic key authentication / ip restriction
* takes care of type-conversion
* provides inheritance (create abstract namespaces and use them as superclasses)
* supports multiple versions of one API
* provides several output formats (json, jsonp, xml, etc.)
* can form output for several usages (ie. ExtJS forms, etc.)
* has features for: *caching, throttling, pickling*
* can be extended with your own features

Client features:

* super simple access to server functions
* an easy switch between different api versions

Installation
============

::
    
    easy_install -U django-simpleapi

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

Server example
==============

First example
-------------

Let's start with our first simple server implementation. See more below in this README.

handlers.py::

    from simpleapi import Namespace

    class JobNamespace(Namespace):
        def status(self, job_id):
            # get the job by job_id ...
            return job.get_status()
        status.published = True # make the method available via API

    class SMSNamespace(JobNamespace):
        def new(self, to, msg, sender='my website', priority=5):
            # send sms ...
        new.published = True # make the method available via API
        new.constraints = {'priority': int} # ensure that priority argument is of type int

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

    from datetime import datetime
    from simpleapi import Namespace, Response, ResponseElement

    class JobNamespace(Namespace):
        # you can either use a callable here or provide a list of ip addresses:
        __ip_restriction__ = ["127.0.0.*", "78.47.135.*"]

        # you can either use a callable here (for dynamic authentication) or provide a static key for authentication:
        __authentication__ = "91d9f7763572c7ebcce49b183454aeb0"

        def _get_job_by_id(self, job_id):
            # get the job by job_id
            # this method isn't published to the public and isn't
            # made accessable via API since it's missing the published-flag
            return Job.objects.get(id=job_id)

        def status(self, job_id):
            job = self._get_job_by_id(job_id)
            return job.get_status()
        status.published = True # make the method available via API
        status.constraints = {'job_id': str}

    class FaxNamespace(JobNamespace):
        #Send a fax and use a the provided Response object to built a response that
        #can be sent as json/jsonp/xml and parse back to a Response on a python or javascript client
        #The Response object is modeled after ElementTree

        ret = Response()

        #send fax
        if not success:
            ret.add_error("The Fax failed to send")
        else:
            el = ResponseElement("receipts")
            el.text = "The fax was sent on {date}".format(date=datetime.now())

        return ret


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
        new.constraints = {'priority': int, 'phonenumber': re.compile(r'\+\d{1,4}\ \d{3,6} \d{5,}')} # ensure that priority argument is of type int

urls.py::

    from simpleapi import Route
    from handlers import OldSMSNamespace, NewSMSNamespace, FaxNamespace

    urlpatterns = patterns('',
        (r'^job/fax/$', Route(FaxNamespace)), # Route with exact one namespace
        (r'^job/sms/$', Route(OldSMSNamespace, NewSMSNamespace)), # Route can hold different versions of namespaces
    )

The namespace with the highest version is the default one which will be used when the client doesn't provide a version.

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

Namespace methods
-----------------

In order to make a method available and callable from outside (the client party) and to configure the called method `simpleapi` reads some configuration variables for each method. They are configured as follows::

    class MyNamespace(Namespace):
        def my_api_method(self, arg1):
            return arg1
        my_api_method.configuration_var = value # <--

The following configuration parameters are existing:

:published: make the method available and callable from outside (boolean)
:constraints: a dict where you can specify any type of which one parameter must be of. The parameter will be converted into your desired type (if simpleapi cannot, it wil raise an error to the client). You can also define a callable (which gets (`namespace`, `value`) passed and must return the new value or any error, like ValueError) or a compiled regular expression (`re.compile(r'...')`; in this case the value will be checked against the regular expression). See the examples for more.
:methods: specifies which HTTP methods are allowed to call the method (a list; by default it allows every method). If you plan to receive a huge amount of data (like a file), you should only allow POST as this can manage "unlimited" data (GET is limited to 1024 bytes which is fairly enough for much function calls though).
:outputs: if specified, the output formatters are limited for this method (a list; e. g. useful, if you plan to return values that cannot be serialized by the json-module but can be pickled and compatibility to Ajax and others isn't an issue for you)

Namespace configuration
-----------------------

You can configure your namespaces on an individual basis. This are the supported configuration parameters:

:__version__: an integer; important if you want provide different versions of namespaces within one Route (e. g. for introducing improved API methods without breaking old clients which uses the old namespace, see example above). If the client doesn't provide a version, the namespace with the highest will be used.
:__ip_restriction__: either a list of ipaddresses (which can contain wildcards, e.g. `127.*.0.*`) which are allowed to access the namespace or a callable which takes the ipaddress as an argument and returns `True` (allowed) or `False` (disallowed). Can be used to keep track of all requests to this namespace and to throttle clients if needed, for example.
:__authentication__: either a string with a key or a callable which takes the access_key provided by the client. Must return `True` (allowed) or `False` (disallowed). If not given, no authentication is needed. It's recommended to use SSL if you plan to use `__authentication__`.
:__outputs__: If given, the namespace is restricted to the given output formatters (a list of strings)
:__inputs__: If given, the namespace is restricted to the given input formatters (a list of strings)
:__features__: list of activated namespace-features (currently available: `throttling`, `caching`)

All parameters are optional.

NamespaceSession
----------------

An individual connection-based `NamespaceSession` is provided within any method call and can be reached via `self.session`. The following parameters are available:

:request: the original request object provided by django
:access_key: client's access key
:version: client's requested version
:mimetype: the mimetype which will be used for the response

Note: All properties are **read-only**. Any changes made will be ignored.

Example call::

    print self.session.access_key

Route configuration
-------------------

The `Route` maintains the communcation between calling clients and your API implementation, the `Namespace`. It is hooked on a specific URL in your `urls.py` like this::

    (r'^job/fax/$', Route(FaxNamespace))

`Route` takes only `namespaces` as arguments. If you have different versions of `namespaces` (see `__version__` in *Namespacce configuration*) you can pass as many `namespaces` as you want to `Route`. It will manage automatically all versions and will use the right one for incoming method calls from clients.

This is an example with 2 different namespacs, a basic one (version 1) and a extended one (verison 2), which would break clients which are developed for version 1.

::

    class BookingSystem(Namespace):
        # global configuration for all derived BookingSystem-classes
        pass

    class BookingSystem_1(BookingSystem):
        __version__ = 1

    class BookingSystem_2(BookingSystem):
        __version__ = 2

Your urls.py should look like::

    (r'^api/$', Route(BookingSystem_1, BookingSystem_2))

Whenever a new client wants to use your API without providing a specific version he will be connected to the `namespace` with the highest version number (in our example version 2). If he provides version *1*, he will see automatically `BookingSystem_1`, if he provides *2*, he will get in touch with `BookingSystem_2`.

In `simpleapi's` client you can use `set_version()` or the `version`-argument at instantiation to define which version you want to use (see example project). The related HTTP parameter is called `_version` (see *HTTP call and parameters* for more).

HTTP call and parameters
------------------------

Clients are able to call the procedures like::

    http://www.yourdomain.tld/job/sms/?_call=new&to=012345364&msg=Hello!&sender=from+me
    http://www.yourdomain.tld/job/sms/?_call=status&_output=xml&job_id=12345678

The following parameters are used by simpleapi:

:_call: method to be called
:_output: output format (e. g. xml, json; default is json)
:_input: input format
:_data: instead of passing every single argument as an own http parameter, you can pass a dictionary/array to _data instead (_input must be defined then; json is recommended). 
:_version: version number of the API that should be used (see *`Route` configuration*)
:_access_key: access key to the API (only if `__authentiation__` in `namespace` is defined)
:_callback: defines the callback for JSONP (default is `simpleapiCallback`)
:_mimetype: `simpleapi` automatically sets the correct mime type depending on the desired output format. you can set a different mimetype by set this http parameter.

Server's response
-----------------

If you call a method the server will response as follows:

:status: true or false (boolean; indicates whether the call was successful or not)
:result: return value of the called function (only if the call was **successful**)
:errors: contains reasons why the call was **not successful** (list of unicode strings)

Usage in web-apps
-----------------

Imagine the following server implementation which will be used for the web-app examples::

    from simpleapi import Namespace

    class Calculator(Namespace):
        def multiply(self, a, b):
            return a*b
        multiply.published = True
        multiply.constraints = {'a': float, 'b': float}

        # example for user-defined callable for the constraints-property
        def check_power(self, key, value):
            # you can even check the values when you accept **kwargs
            # in your API method
            return float(key) # return casted value # simpleapi will take care of any errors raised

        def power(self, a, b):
            return a**b
        power.published = True
        power.constraints = check_power

The next two chapters are covering Ajax (with jQuery) and crossdomain-Requests.

Usage in web-apps (Ajax+jQuery)
-------------------------------

If your functions are not limited to an specific output formatter (which is the default) you're able to call the functions (within the same domain) via Ajax (XMLHttpRequest). I prefer using jQuery or ExtJS which makes calling remote functions a snap. The following example is using jQuery::

    jQuery.get("/myapi/", {_call: 'multiply', a: 5, b: 10}, function (result) {
        alert('5 * 10 = ' + result);
    })

For more informaton on jQuery's ajax capabilities see here: http://api.jquery.com/category/ajax/

See the demo project for an example implementation.

Usage in web-apps (crossdomain)
-------------------------------

If you want to call an API method from a third-party page (which isn't located on the same domain as the server API) you cannot use XMLHttpRequest due to browser security restrictions.

In this case you can use simpleapi's JSONP implementation which allows you to call functions and get the result back via a callback. Some Ajax implementations (like jQuery and ExtJS) support transparent Ajax requests which internally uses the <script>-tag to get access to the remote function. In jQuery it looks like::

    $.ajax({
        url: "http://127.0.0.1:8888/api/calculator/one/",
        data: {_call: 'multiply', a: 5, b: 10},
        dataType: "jsonp",
        jsonp: "_callback", // needed since simpleapi names his callback-identifier "_callback"
        success: function (result) {
            alert('5 * 10 = ' + result);
        }
    })

See the demo project for an example implementation.

Usage of simpleapi's client
---------------------------

The client's class lives in `simpleapi.Client`. Import it from there and instantiate your client like this::

    my_client = Client(ns='http://yourdomain.tld/api/namespace/')

To call a remote function you just use call it the same as you do usually::

    my_client.my_remote_function(first="first argument", second_arg=2, third=datetime.datetime.now())

**Hint:** It's important that you name your arguments, anonymous arguments are prohibited.

The constructor takes following optional arguments:

:version: defines the version to be used (if no one is given, the default API version is used)
:access_key: defines the access key to the API
:transport_type: Change transport type (default is `json`). You can set 'pickle' here if the other side allows it (pickle must be added to `__output__`).

Following methods are provided by client instances:

:set_ns: set's a new namespace-URL to be used
:set_version: changes the version to be used

Following exceptions can be raised by the client instance:

:ConnectionException: there was a problem during connection establishment or transmission
:RemoteException: a remote exception was raised

Usage of arguments and \*\*kwargs in your API method
---------------------------------------------------

Usually your namespace method looks like this::

    def my_api_method(self, a, b, c, d=10):
        return a+b+c+d
    my_api_method.published = True

In the request this would cause the following: `?a=1&b=2&c=3` (d is optional).

If you are in need to get "unlimited" parameters you can also use `\*\*kwargs` (not `*args`!) in your API method like this::

    def sum_it_up(self, **kwargs):
        return sum(map(lambda item: int(item), kwargs.values()))
    my_api_method.published = True

`kwargs` contains all unused parameters. If the request looks like `?var1=195&var2=95&var3=9819&var999=185` `kwargs` contains all these parameters.

**Advice**: To check the **kwargs values use a callable for the method's `constraints`-configuration.

**Hint**: If you're passing more parameters in your client call than your function signature contains (e. g. in our first example only `a, b, c and d`) and your function doesn't contain a `\*\*kwargs`, the client call will fail with an appropriate errormessage.

Error handling on client/server-side
------------------------------------

If you want to raise an error and abort execution of your method you can always call `self.error(err_or_list)`. `err_or_list` is either an unicode string or a list of unicode strings.

In simpleapi client: `self.error` raises a `simpleapi.RemoteException` which you can catch to handle the error on the client side (see example for more).

Supported formatters
--------------------

* value ("value")
* JSON ("json", default)
* JSONP ("jsonp")
* cPickle ("pickle") - **should only be used by trusted parties**
* XML ("xml")

Supported wrappers
------------------



Features (take your namespace to a higher level)
================================================

Features are adding more functionality and capability to your namespace. There are a few built-in features, but the `__features__`-configuration especially allows **you** to extend **your** namespace. It looks like this::

    class MyNamespace(Namespace):
        __features__ = ['throttling', 'caching', MyVeryOwnFeature]

Please see the example projects for a demo use and implementation of Features.

Caching
-------

simpleapi supports caching of function calls. This is pretty useful when you have a lot of calls to cpu/memory/db-intensive methods. You can ask simpleapi to cache the response (the return value) of a function call depending on the given function arguments. To do so, first add `caching` to the list of namespace-features::

    __features__ = ['caching']

Using the namespace-method `caching`-configuration you can configure how the `simpleapi`-cache will work::

    def delayed_function(self):
        import time
        time.sleep(5)
        return True
    delayed_function.published = True
    delayed_function.caching = {
        'timeout': 30, # in seconds
        'key': 'delayed_function'
    }

The `caching`-option can either be a boolean or a dictionary with user-defined settings. `Timeout` defines, after which timeperiod the key will be removed (default is 1 hour). The `key` defines the caching-key (default-format `simpleapi_FUNCTIONNAME`) which can either be a string or a callable (with the `request` object passed).

A md5-generated fingerprint of the given arguments will be appended to the caching key. If your user-defined caching key is *delayed_function*, the complete key might be *delayed_function_0cc175b9c0f1b6a831c399e269772661*. The return value of the function is stored pickled.

**Note:** Don't forget to configure Django for caching (especially CACHE_BACKEND), see more: http://docs.djangoproject.com/en/dev/topics/cache/

Throttling
----------

simpleapi supports throttling by default. Add `throttling` to `__features__` to activate. You can throttle both single methods and namespace calls in general by number of calls per second, minute and hour per client. Please see the example project for a demo implementation.

simpleapi uses django's caching ability. It's recommended that you use a cache backend which supports atomic updates and is pretty fast (ie. memcached).

How to run the demo
===================

1. Start the server with `./manage.py runserver 127.0.0.1:8888`
2. Start the client `python testclient.py`

(Make sure simpleapi is in your PATH)

Tips & tricks
=============

#. Take a look on my example project (example_project/[client|server]) for a first view on how simpleapi works.
#. Make sure to remove or deactivate the new csrf-middleware functionality of django 1.2 for the Route.
#. Use SSL to encrypt the datastream.
#. Use key authentication, limit ip-address access to your business' network or server.
#. You can set up a simple throtteling by setting a callable to `__ip_restriction__` which keeps track on every request of an ip-address (the callable gets the ip-address of the calling party as the first argument).
#. You can outsource your namespace's settings by creating new vars in your local settings.py file (e. g. `NAMESPACE_XY_IP_RESTRICTIONS=["127.0.0.*", ]`) and reference them within your namespace (like `__ip_restriction__ = settings.NAMESPACE_XY_IP_RESTRICTIONS`)

Limitations
===========

#. The output/return value of a method is limited to the formatter's restrictions. For instance, you cannot return datetime values since they aren't supported by JSON (use datetime.isotime() or datetime.ctime() instead). Applies only if you're not using cPickle in an trusted environment (which supports datetime-objects and more).