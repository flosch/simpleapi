=====================
Python client library
=====================

``simpleapi`` ships with a Python client library which makes the communication between Python apps a snap. It's absolutely seamless, transparent and easy to use. This is how a remote call looks like on the client side::

    from simpleapi import Client

    client = Client(ns='http://birthdayservice.tld/api/')
    print "Mom's birthday is on:", client.get_birthday("Mom").ctime()

``ns`` takes the URL of your API. It can either be a ``http`` or  a ``https`` (preferred) address for a secure connection.

As you can see ``simpleapi`` can work with data objects (for instance ``datetime``-objects). In special this depends on the used data protocol (for example JSON, XML, Pickle, etc.), but the common data types like ``strings``, ``integers``, ``floats``, ``lists``, ``dicts`` and ``datetimes`` are supported by all of them. For more limitations on transport types see :ref:`limitations`.

By default, the Python client library uses JSON as a transport type (for requests as well as responses), but you're free to change that by passing the ``transport_type`` parameter to the constructor containing your desired formatter name. For available built-in formatters (or writing your own ones), see the :ref:`messages` documentation part.

Multiple versions of ``Namespaces``
-----------------------------------

``simpleapi`` supports multiple versions of ``Namespaces`` (e. g. for the case that your API evolves over time and existing method behaviour changes). By default, the client automatically uses the latest provided version. If you want to stay at one ``Namespace`` version and want to use it anytime, you can supply your desired version number by passing it to the ``version`` argument of client's constructor.

Authentication
--------------

If your ``Namespace`` requires an authentication key you can supply one using the ``access_key`` parameter passing to the client's constructor. There's nothing special about that. If the authentication fails, the client will raise a ``RemoteException`` (see more below for Exception handling).

Long running calls
------------------

For remote calls which take long time to proceed (for example a newsletter which is send to a bunch of recipients and your client application is still waiting for an OKAY) the constructor has a ``timeout`` parameter which takes the desired response timeout in seconds (default depends on your system's configuration). Set it as high as you want and as your system support it, e.g. ``timeout = 600`` for 10 minutes. 

Exception handling
------------------

To handle connection problems or remote exceptions the client raises two types of errors: ``ConnectionException`` and ``RemoteException``. The client library throws a ``ConnectionException`` whenever there are problems with receiving the data from the given URL. These exceptions are covering all the network communication stuff, instead of ``RemoteException`` which basically raises when the client reaches the API but the specific call fails (in all situations like authentication failed, wrong parameters, user-generated errors).

In both situations the exception message contains more information about the error (especially the error message in most cases).