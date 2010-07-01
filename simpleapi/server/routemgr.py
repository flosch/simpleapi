# -*- coding: utf-8 -*-

from simpleapi.message.common import SAException

__all__ = ('RouteMgr', )

class RouteMgrException(SAException): pass
class RouteNotFound(RouteMgrException): pass
class RouteMgr(object):
    def __init__(self, *routes):
        self.routes = {}
        for route in routes:
            self.routes[route.name] = route
    
    def __call__(self, *args, **kwargs):
        route_name = kwargs.pop('name')
        if self.routes.has_key(route_name):
            return self.routes[route_name](*args, **kwargs)
        raise RouteNotFound(route_name)