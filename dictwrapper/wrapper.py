from collections.abc import MutableMapping


class DictWrapper(MutableMapping):
    """A dictionary wrapper to allow customization"""

    def __init__(self, *args, **kwargs):
        self.store = dict()
        self.update(dict(*args, **kwargs))

    def __getitem__(self, key):
        return self.store[key]

    def __setitem__(self, key, value):
        self.store[key] = value

    def __delitem__(self, key):
        del self.store[key]

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

    def __contains__(self, item):
        return item in self.store

    def keys(self):
        """Access the dictionary keys"""
        return self.store.keys()

    def values(self):
        """Access the dictionary values"""
        return self.store.values()

    def __repr__(self):
        return f"{self.__class__.__name__}({self.store.__repr__()})"
