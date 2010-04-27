# -*- coding: utf-8 -*-

import re, random
from simpleapi import Namespace
from sapi.message import Message, MessageElement

class Example(Namespace):
    __version__ = 1

    def test(self, username):
        root = MessageElement('messages', to=username)

        for i in xrange(random.randint(1, 10)):
            el = MessageElement('message')
            el.text = 'Message #%s' % random.randint(1, 5000)
            el.set('type', 'public')
            if random.randint(1, 5000) > 3000:
                el.set('type', 'private')
            el.set('from', random.choice(['Al', 'Dj', 'Frank', 'John']))
            root.append(el)

        return Message(root)
    test.published = True
    test.methods = ('POST',)
