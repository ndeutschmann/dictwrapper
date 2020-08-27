"""A nested dictionary like structure that allows flat access to its whole structure"""

from dictwrapper import DictWrapper


class MultipleKeyError(KeyError):
    """Signals that a nested mapping contains the same key multiple times"""


class NestedMapping(DictWrapper):
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
        return self.find_store_(item)[item]

    def __setitem__(self, key, value):
        """Edit existing entries at any level, add new keys at the top level only.
        Raise an error if multiple entries exist for this key.

        Raises
        ------
        MultipleKeyError: if the input key matches several entries in the structure
        """
        try:
            self.find_store_(key)[key] = value
        except KeyError:
            self.store[key] = value

    def find_store_(self, key):
        """find the underlying dictionray matching a key at any level

        Parameters
        ----------
        key : hashable object

        Returns
        -------
        dict
            The `store` attribute containing the key


        Raises
        ------
        MultipleKeyError: if the input key matches several entries in the structure
        KeyError: if no key match the input
        """
        found = False
        result = None
        # Try the current toplevel
        if key in self.store:
            result = self.store
            found = True

        # Look at all sublevel
        branches = [self.store[item] for item in self.store if isinstance(self.store[item], NestedMapping)]
        for branch in branches:
            try:
                result = branch.find_store_(key)
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

