================
Raw HTTP request
================

``simpleapi`` communicates using HTTP and therefore takes some parameters which will be discussed here.

Sample call::

    /api/?_call=multiply&_access_key=foobar&a=5&b=11

:_call: method name (from the ``Namespace`` you're calling)
:_access_key: Key to access the ``Namespace`` (default: *empty*)
:_callback: When using JSONP, defines the callback function (default:  ``simpleapiCallback``).
:_mimetype: Individual mimetype differing from the default one (*note:* simpleapi sets the correct mimetype depending on your desired output format). *Hint*: If you want to see the response in your browser (instead of download like some browsers want to), set the mimetype to ``text/html``.
:_data: Takes an object containing all function parameters (default: *empty*). See below for more.
:_version: Defines which version of your ``Namespaces`` to use (default: *latest*).
:_input: Format type (see :ref:`formatters`) to use (e. g. ``JSON``, ``JSONP``, ``XML``, etc.) for the request parameters (default: *value*, see below)
:_output: Format type (see :ref:`formatters`) to use (e. g. ``JSON``, ``JSONP``, ``XML``, etc.) for the response (default: *JSON*)
:_wrapper: Wrapper name of the wrapper to use to form the response (see :ref:`wrappers`).

All parameters except ``_call`` are optional.

Method arguments
----------------

If you call a method, you frequently have to pass arguments to the method. In ``simpleapi`` you can do this in two ways. 

Either you just append the parameter to your HTTP call (like ``a`` and ``b`` in the sample call above) or you use the ``_data`` http parameter to provide an object (a dictionary/associative array) with your parameters inside. 

Regardless which way you use, you have to **encode** your parameters depending on your ``_input`` http parameter. By default, there's no input-encoding set (hence you can pass your arguments plain). Note that you've to set an input encoding since *value* (plain) is prohibited when using the ``_data`` parameter.