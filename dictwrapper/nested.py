"""A nested dictionary like structure that allows flat access to its whole structure"""

from collections import UserDict
from collections.abc import Iterator
from .wrapper import DictWrapperStub


class MultipleKeyError(KeyError):
    """Signals that a nested mapping contains the same key multiple times"""


class NestedIterator(Iterator):
    """Iterator for looping depth first through the leaves of a nested mapping"""

    def __init__(self, mapping):
        assert isinstance(mapping, NestedMapping)
        self.mapping = mapping
        self.iter_stack = [iter(mapping.data)]

    def __next__(self):
        if len(self.iter_stack) == 0:
            raise StopIteration
        try:
            next_key = next(self.iter_stack[-1])
            next_value = self.mapping[next_key]
            if isinstance(next_value, NestedMapping):
                self.iter_stack.append(iter(next_value.data))
                return self.__next__()
            else:
                return next_key
        except StopIteration:
            self.iter_stack.pop(-1)
            return self.__next__()


class NestedMapping(DictWrapperStub):
    """A nested dictionary structure whose leaf keys are all accessible from the top level for read and write
    provided they are unique.

    This class implements the MutableMapping interface as if all terminal mappings were in the top-level dictionary,
    ignoring any intermediate keys. For example

    {
        "a": 1,
        "sublevel": {
            "b": 2
        }
    }

    behaves just as

    {
        "a": 1,
        "b": 2
    }

    Notes
    -----
    This is implemented with a full tree traversal at each read/write so it is a much worse container than
    a dictionary for fast access. Use this for small data used infrequently (it is designed to hold configurations
     and be used at initialization/wrap-up).
    """

    def __getitem__(self, item):
        """Look for the key in the current level, otherwise look for it in the sublevels

        Raises
        ------
        MultipleKeyError: if the input key matches several entries in the structure
        KeyError: if no key match the input
        """
        return self.find_data_(item)[item]

    def __setitem__(self, key, value):
        """Edit existing entries at any level, add new keys at the top level only.
        Raise an error if multiple entries exist for this key.

        Raises
        ------
        MultipleKeyError: if the input key matches several entries in the structure
        """
        try:
            self.find_data_(key)[key] = value
        except KeyError:
            self.data[key] = value

    def __delitem__(self, key):
        del self.find_data_(key)[key]

    def __iter__(self):
        return NestedIterator(self)

    def __len__(self):
        current_len = len(self.data)
        children = self.get_children()
        if len(children) == 0:
            return current_len

        current_len -= len(children)
        return current_len + sum([len(child) for child in children])

    def get_children(self):
        return [self.data[item] for item in self.data if isinstance(self.data[item], NestedMapping)]

    def get_leaves(self):
        return [self.data[item] for item in self.data if not isinstance(self.data[item], NestedMapping)]

    def find_data_(self, key):
        """find the underlying dictionary matching a key at any level

        Parameters
        ----------
        key : hashable object

        Returns
        -------
        dict
            The `data` attribute containing the key


        Raises
        ------
        MultipleKeyError: if the input key matches several entries in the structure
        KeyError: if no key match the input
        """
        found = False
        result = None
        # Try the current toplevel
        if key in self.data:
            result = self.data
            found = True

        # Look at all sublevel
        branches = self.get_children()
        for branch in branches:
            try:
                result = branch.find_data_(key)
                if found:
                    raise MultipleKeyError(key)
                else:
                    found = True
            except KeyError:
                pass

        if found:
            return result
        else:
            raise KeyError(key)
