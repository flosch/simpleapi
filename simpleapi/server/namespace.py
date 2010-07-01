# -*- coding: utf-8 -*-

from simpleapi.message.common import json
from response import UnformattedResponse

__all__ = ('Namespace', 'NamespaceException')

class NamespaceException(Exception): pass
class Namespace(object):

    def __init__(self, request):
        self.request = request
        self.session = request.session

    def error(self, errors):
        raise NamespaceException(errors)

    def introspect(self, framework='default'):
        if framework not in ['default', 'extjsdirect']:
            self.error('Framework unknown.')

        functions = []
        
        version = getattr(self, '__version__', 'default')
        function_map = self.request.route.nmap[version]['functions']
        
        for fn in function_map.iterkeys():
            functions.append({
                'name': fn,
                'len': len(function_map[fn]['args']['obligatory']),
                'formHandler': False,
            })

        result = {
            'actions': {
                self.request.route.name: functions
            }
        }

        if framework == 'extjsdirect':
            return UnformattedResponse(
                content=u'Ext.app.REMOTING_API = %s' % json.dumps(result),
                mimetype='text/javascript'
            )

        return result
    introspect.published = True