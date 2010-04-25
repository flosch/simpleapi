from simpleapi import wrappers, Wrapper

from message import Message

class MessageWrapper(Wrapper):
    def build(self):
        if isinstance(self.result, Message):
            result = self.result
        else:
            result = Message(self.result)

        if self.errors:
            result.success = False
        else:
            result.success = True

        result._errors = self.errors
        return result
wrappers.register('message', MessageWrapper)
