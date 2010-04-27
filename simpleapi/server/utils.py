# -*- coding: utf-8 -*-

from fnmatch import fnmatch

__all__ = ('glob_list', )

class glob_list(list):
    """A list which is Unix shell-style wildcards searchable"""
    def __contains__(self, key):
        for elt in self:
            if fnmatch(key, elt): return True
        return False
