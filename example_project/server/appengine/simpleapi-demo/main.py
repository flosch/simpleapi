#!/usr/bin/env python

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

from simpleapi import Route
from handlers import MyAPI

def main():
    application = webapp.WSGIApplication(
        [('/api/', Route(MyAPI, framework='appengine'))]
    )
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
