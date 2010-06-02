#!/usr/bin/env python

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

from simpleapi import Route
from handlers import MyAPI

class MyRequestHandler(webapp.RequestHandler):
    def get(self):
        self.response.out.write("huhu %s" % self.request.get("name"))

def main():
    application = webapp.WSGIApplication(
        [('/api/', Route(MyAPI, framework='appengine')),
         ('/', MyRequestHandler)],
        debug=True
    )
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
