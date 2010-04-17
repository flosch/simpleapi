# -*- coding: utf-8 -*-

from fnmatch import fnmatch

class glob_list(list):
	def __contains__(self, key):
		for elt in self:
			if fnmatch(key, elt): return True
		return False