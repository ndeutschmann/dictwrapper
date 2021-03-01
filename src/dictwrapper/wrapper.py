from collections import UserDict
from collections.abc import MutableMapping
from abc import ABC
import pandas as pd


class DictWrapperStub(MutableMapping, ABC):
    def __init__(self, *args, **kwargs):
        self.data = dict()
        self.update(*args, **kwargs)

    def copy(self):
        return self.__class__(self.data.copy())

    __copy__ = copy

    def __repr__(self):
        return f"{self.__class__.__name__}({self.data.__repr__()})"

    def as_dict(self):
        """Represent the data as a dictionary"""
        return dict(self.items())

    def as_dataframe(self):
        """Represent the data as a pandas Dataframe with a single row"""
        return pd.DataFrame([self.values()], columns=self.keys())


class DictWrapper(DictWrapperStub, UserDict):
    pass
