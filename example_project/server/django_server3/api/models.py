# -*- coding: utf-8 -*-

from django.db import models

class Contact(models.Model):
    
    name = models.CharField(max_length=150)
    phone = models.CharField(blank=True, null=True, max_length=50)
    fax = models.CharField(blank=True, null=True, max_length=50)