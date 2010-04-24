# -*- coding: utf-8 -*-

class Wrapper(object):
    
    def __init__(self, errors, result):
        if isinstance(errors, basestring):
            errors = [errors,]
        self.errors = errors

        if self.errors:
            assert isinstance(self.errors, (list, tuple))
        
        self.result = result
    
    def build(self):
        raise NotImplemented

class DefaultWrapper(Wrapper):
    
    def build(self):
        result = {}
        if self.errors:
            result['success'] = False
        else:
             result['success'] = True
        if self.errors:
            result['errors'] = self.errors
        if self.result:
            result['result'] = self.result
        return result

class ExtJSFormWrapper(Wrapper):
    
    def build(self):
        result = {}
        if self.errors:
            result['success'] = False
        else:
             result['success'] = True
        if self.errors:
            errmsg, errors = self.errors[0], self.errors[1]
            assert isinstance(errmsg, basestring)
            assert isinstance(errors, dict)
            
            result['errormsg'] = errmsg
            result['errors'] = errors
        if self.result:
            result['data'] = self.result
        return result

__wrappers__ = {
    'default': DefaultWrapper,
    'extjsform': ExtJSFormWrapper
}