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

    def introspect(self, framework='default', provider='Ext.app',
                   namespace=None):
        if framework not in ['default', 'extjsdirect']:
            self.error('Framework unknown.')

        version = getattr(self, '__version__', 'default')
        function_map = self.request.route.nmap[version]['functions']

        if framework == 'extjsdirect':
            functions = {}
            for cls in ('forms', 'direct'):
                functions[cls] = []
                for fn in function_map.iterkeys():
                    if len(function_map[fn]['args']['all']) > 0:
                        fnlen = 1
                    else:
                        fnlen = 0

                    functions[cls].append({
                        'name': fn,
                        'len': fnlen,
                        'formHandler': cls == 'forms',
                    })

            result = {
                'actions': {
                    self.request.route.name: functions['direct'],
                    u'%s_forms' % self.request.route.name: functions['forms'],
                }
            }

            result['type'] = 'remoting'
            result['url'] = u'%s?_wrapper=extjsdirect' % \
                self.session.request.path_info
            if namespace:
                result['namespace'] = namespace
            return UnformattedResponse(
                content=u'%s.%s_REMOTING_API = %s;' %\
                    (provider, self.request.route.name.upper(),
                     json.dumps(result)),
                mimetype='text/javascript'
            )
        else:
            functions = []
            for fn in function_map.iterkeys():
                print function_map[fn]['args']
                optionals = list(set(function_map[fn]['args']['all']) - \
                    set(function_map[fn]['args']['obligatory']))
                functions.append({
                    'name': fn,
                    'args': {
                        'len': len(function_map[fn]['args']['all']),
                        'obligatory': {
                            'len': len(function_map[fn]['args']['obligatory']),
                            'names': function_map[fn]['args']['obligatory'],
                        },
                        'optional': {
                            'len': len(optionals),
                            'names': optionals,
                        },
                        'kwargs_allowed': function_map[fn]['args']['kwargs_allowed'],
                    },
                })

            result = {
                'actions': {
                    self.request.route.name: functions
                }
            }

        return result