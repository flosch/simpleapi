# -*- coding: utf-8 -*-

from simpleapi.message.common import json, SAException
from response import UnformattedResponse

__all__ = ('Namespace', 'NamespaceException')

class NamespaceException(SAException): pass
class Namespace(object):

    def __init__(self, request):
        self.request = request
        self.session = request.session

    def error(self, *errors):
        errors = list(errors)
        if len(errors) == 1:
            errors = errors[0]
        raise NamespaceException(errors)

    def introspect(self, framework='default', provider='Ext.app', namespace=None):
        if framework not in ['default', 'extjsdirect']:
            self.error('Framework unknown.')

        functions = []
        
        version = getattr(self, '__version__', 'default')
        function_map = self.request.route.nmap[version]['functions']
        
        for fn in function_map.iterkeys():
            if fn in ['introspect', ]: continue
            
            if len(function_map[fn]['args']['all']) > 0:
                fnlen = 1
            else:
                fnlen = 0
            
            functions.append({
                'name': fn,
                'len': fnlen,
                'formHandler': True,
            })

        result = {
            'actions': {
                self.request.route.name: functions
            }
        }

        if framework == 'extjsdirect':
            result['type'] = 'remoting'
            result['url'] = u'%s?_wrapper=extjsdirect' % \
                self.session.request.path_info
            if namespace:
                result['namespace'] = namespace
            return UnformattedResponse(
                content=u'%s.REMOTING_API = %s;' %\
                    (provider, json.dumps(result)),
                mimetype='text/javascript'
            )

        return result
    introspect.published = True