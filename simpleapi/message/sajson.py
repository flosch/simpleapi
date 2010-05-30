# -*- coding: utf-8 -*-

import json
import re
import datetime
from dateutil.parser import parse

__all__ = ('SimpleAPIEncoder', 'SimpleAPIDecoder')

date_re = re.compile(r'\w{2,}\ \w{2,} \d{1,}')
#Sun May 30 00:00:00 2010

time_re = re.compile(r'\d{1,2}\:\d{1,2}\:\d{1,2}')
#19:36:20.412047

class SimpleAPIEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.ctime()
        elif isinstance(obj, datetime.time):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)

class SimpleAPIDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        super(SimpleAPIDecoder, self).__init__(*args, **kwargs)
        self.object_hook = self.hook

    def hook(self, obj):
        for key, val in obj.iteritems():
            if isinstance(val, basestring) and (date_re.match(val) \
                or time_re.match(val)):
                try:
                    obj[key] = parse(val)
                except ValueError:
                    pass
                else:
                    if time_re.match(val):
                        obj[key] = obj[key].time()
        return obj