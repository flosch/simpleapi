.. _limitations:

============================
Limitations and work-arounds
============================

JSON and datetimes
------------------

By default, JSON does not support datetimes as a data type. ``simpleapi`` takes care of this automatically and converts any ``datetime``, ``date`` and ``time`` objects to a special format which is supported by JavaScript's ``Date``-object.

If your ``Namespace`` method returns a datetime like::

    datetime.datetime(2010, 6, 2, 12, 0, 35, 377674)

``simpleapi`` will converts this into the following string representation::

    Wed Jun  2 12:00:58 2010.

In JavaScript you can simply create a ``Date``-object by passing the converted string to the constructor like this

.. code-block:: javascript

    new Date("Wed Jun  2 12:00:58 2010")

The ``Date``-object will parse the string and convert it. 

Between both the ``simpleapi`` server and the **Python client** working with datetimes is absolutely seamless and transparent. As seen the server will convert the ``datetime`` into a string representation and the Python client (unfortunately not the PHP client yet) will detect this string representation and will convert it back into appropriate ``datetime``, ``date`` and ``time`` objects.