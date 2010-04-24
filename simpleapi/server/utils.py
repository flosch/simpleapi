# -*- coding: utf-8 -*-

from fnmatch import fnmatch

__all__ = ('glob_list', )

class glob_list(list):
    def __contains__(self, key):
        for elt in self:
            if fnmatch(key, elt): return True
        return False