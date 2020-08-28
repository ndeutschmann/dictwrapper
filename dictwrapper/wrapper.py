from collections import UserDict
from collections.abc import MutableMapping
from abc import ABC


class DictWrapperStub(MutableMapping, ABC):
    """"""
    def __init__(self, *args, **kwargs):
        self.data = dict()
        self.update(*args, **kwargs)

    __copy__ = UserDict.__copy__
    copy = UserDict.copy

    def __repr__(self):
        return f"{self.__class__.__name__}({self.data.__repr__()})"


class DictWrapper(DictWrapperStub, UserDict):
    pass
