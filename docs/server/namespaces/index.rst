.. _namespaces:

==========
Namespaces
==========

Namespaces contain your business logic. They are normal Python classes and are being implemented very intuitively. Here's how an example looks like::

    import urllib
    import re
    from simpleapi import Namespace

    class Downloader(Namespace):
        def download(self, url):
            """Downloads a webpage and returns the full sourcecode."""
            try:
                response = urllib.urlopen(url)
                print response.getcode()
            except IOError, e:
                self.error(unicode(e))
            return response.read()
        download.published = True
        download.constraints = {'url':
            re.compile(r'^http\://[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,3}(/\S*)?$')}

As you can see ``simpleapi`` works pretty much like common RPC-implementations. Every method within your ``Namespace`` flagged with the ``published``-keyword set to ``True`` will be exposed by simpleapi to the remote clients. 

For more information on how ``Namespaces`` work see the following subpages.

Contents
========

.. toctree::
   :maxdepth: 2
   
   validation
   session
   authentication
   iprestriction
   errorhandling