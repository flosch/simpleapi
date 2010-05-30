# -*- coding: utf-8 -*-

import datetime

from django.db import models

class Author(models.Model):
    name = models.CharField(max_length=150)

    def natural_key(self):
        return self.name

class Contact(models.Model):
    
    name = models.CharField(max_length=150)
    phone = models.CharField(blank=True, null=True, max_length=50)
    fax = models.CharField(blank=True, null=True, max_length=50)
    datetime_added = models.DateTimeField(default=datetime.datetime.now)

    time_changed = models.TimeField(auto_now=True, auto_now_add=True)
    date_changed = models.DateField(auto_now=True, auto_now_add=True)
    
    author = models.ForeignKey(Author)