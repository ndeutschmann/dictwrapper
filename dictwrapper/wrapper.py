from collections import UserDict
from collections.abc import MutableMapping
from abc import ABC


class DictWrapper(UserDict):
    def __repr__(self):
        return f"{self.__class__.__name__}({self.data.__repr__()})"


class DictWrapperStub(MutableMapping, ABC):
    def __init__(self, *args, **kwargs):
        self.data = dict()
        self.update(*args, **kwargs)
