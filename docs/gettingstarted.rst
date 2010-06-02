===============
Getting Started
===============

The Basics
==========

The Server Implementation
-------------------------

A basic server implementation contains one ``Namespace`` and one ``Route``.
The ``Namespace`` holds all your API logic and implementation, the ``Route``
connects your ``Namespace`` to the world. 

When a client call comes in, ``Route`` will parse the request, checks whether
all required arguments exist and will finally pass them to your method. For
you, the user of ``simpleapi``, ``Route`` is fairly unspectacular. The more
interesting part is the ``Namespace``.

The ``Namespace`` is a bunch of *published* and *non-published* methods. 
*Published methods* are accessable from outside, *non-published* methods are your internally used methods (called *helper functions*). A ``Namespace`` can
have several global and local configuration options for *authentication*,
*ip restrictions*, *type conversion*, *constraints*, *features* (like *caching*, *throttling*, etc.) and *input/output formatters*. Even though the
common way for placing your ``Namespace`` is to use ``handlers.py``, you're
free to put it wherever you like. 

As you already saw on the frontpage, an example implementation of 
``handlers.py`` would look like this::
    
    from simpleapi import Namespace
    
    class Calculator(Namespace):
        def add(self, a, b):
            return a + b
        add.published = True

This is a very easy, but still working calculator with only one function
``add()``. With the local configuration option ``published`` set to ``True``
we export the method ``add()`` to the world. It requires two arguments, ``a``
and ``b``.

To finally make our exported functions available to the world with **django**, we hook up an URL to our ``Route``. ``Route`` takes our ``Namespace`` as an argument.

In this example, the URL ``api/calculator/`` is used to access our Calculator-API::

    from simpleapi import Route
    from handlers import Calculator

    urlpatterns = patterns('',
    	(r'^api/calculator/$', Route(Calculator))
    )

``Route`` takes care of all incoming requests and - in our example - makes sure that the two required arguments ``a`` and ``b`` of our ``add()``-function
exist.

Client Libraries
----------------

``simpleapi`` comes with easy-to-use python and php client libraries which
allows you fully, transparently access to your server implementation. 

With the client libraries, you call the desired remote function as they would
be local. The only difference between a remote call using the library and a
local call are the obligatory named arguments. On every remote call you must 
name your arguments when passing them to the function::
    
    from simpleapi import Client
    
    calculator = Client(ns='http://localhost:8888/api/calculator/')
    print "5 + 3 =", calculator.add(a=5, b=3)

As you can see, the required arguments ``a`` and ``b`` are explicitly named and passed to the function ``add()``. Internally, the client determines which function you want to call, builds an appropriate query and sends the request to the server. The server response is being received and parsed by the client and the return value is passed to you.