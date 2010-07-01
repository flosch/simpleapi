from simpleapi import wrappers, DefaultWrapper

from message import Message

class MessageWrapper(DefaultWrapper):
    def build(self, result, errors):
        if not isinstance(result, Message):
            result = Message(result)

        if errors:
            result.success = False
        else:
            result.success = True

        result._errors = errors
        return result
wrappers.register('message', MessageWrapper)
