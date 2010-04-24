# -*- coding: utf-8 -*-

__all__ = ('Session', )

class Session(object):
    
    def __init__(self, **kwargs):
        self.data = kwargs
    
    def __getattr__(self, name):
        return self.data.get(name)
    
    # python crashes here, still have to be investigated:
    #def __setattr__(self, name, value):
    #    self.data[name] = value
    
    #def __delattr__(self, name):
    #    del self.data[name]