"""A nested dictionary like structure that allows flat access to its whole structure"""
from collections.abc import Iterator
import pandas as pd
import ruamel.yaml as yaml
from copy import deepcopy, copy
from .wrapper import DictWrapperStub


def construct_yaml_tuple(self, node):
    """Constructor function with Instructions to build tuples from YAML files"""
    return tuple(self.construct_sequence(node))


# Register !!python/tuple as a safe instruction in YAML files and associate it
# With our constructor function
yaml.SafeConstructor.add_constructor(
    "tag:yaml.org,2002:python/tuple", construct_yaml_tuple
)


class MultipleKeyError(Exception):
    """Signals that a nested mapping contains the same key multiple times"""


class ProtectedKeyError(Exception):
    """Signals that a key is accessible for reading but not writing"""


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

    def __init__(self, *args, recursive=True, check=True):
        """

        Parameters
        ----------
        args :
            positional argument: either nothing or a valid object for dictionary instantiation
        recursive : bool
            whether to go down the dictionary and convert all sub dictionaries to NestedMappings
        check : bool
            whether to check that the nested structure is valid (i.e. there are no repeated keys)
        """
        super(NestedMapping, self).__init__(*args)
        if recursive:
            for key in self.data:
                if isinstance(self.data[key], dict):
                    self.data[key] = NestedMapping(
                        self.data[key], recursive=True, check=False
                    )

        if check:
            for key in self:
                try:
                    # getitem fails if a key is duplicate
                    self[key]
                except MultipleKeyError as e:
                    raise MultipleKeyError(
                        f"Invalid structure at instantiation: repeated key {key}"
                    ) from e

    @classmethod
    def from_yaml_stream(cls, stream, recursive=True, check=True):
        return cls(yaml.safe_load(stream), recursive=recursive, check=check)

    @classmethod
    def from_yaml(cls, filepath, recursive=True, check=True):
        return cls.from_yaml_stream(
            open(filepath, mode="r"), recursive=recursive, check=check
        )

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
        KeyError: if the input key is not found or is mapped to a substructure of NestedMapping
        """
        try:
            node = self.find_data_(key)
            if isinstance(node[key], NestedMapping):
                raise ProtectedKeyError(key, "Trying to overwrite a subtree")
            node[key] = value
        except KeyError as e:
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
        return current_len + sum([len(child) for _, child in children])

    def get_children(self):
        return [
            (item, self.data[item])
            for item in self.data
            if isinstance(self.data[item], NestedMapping)
        ]

    def get_leaves(self):
        return [
            (item, self.data[item])
            for item in self.data
            if not isinstance(self.data[item], NestedMapping)
        ]

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
        for _, branch in branches:
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

    def copy(self, deep=True):
        """Deep copy by default
        The user is likely to think of the whole nested structure as a single object. By the principle of least
        surprise, we provide the natural behavior in .copy: the whoe structure is copied.

        We keep the shallow __copy__ because a user employing copy.copy (as opposed to copy.deepcopy) is likely
        to really want a shallow copy.
        """
        if deep:
            return deepcopy(self)
        else:
            return copy(self)

    def as_dict(self):
        """Produce a vanilla Python nested dictionnary by going through the whole structure"""
        new_dict = dict()
        new_dict.update(self.get_leaves())

        new_dict.update(
            ((item, child.as_dict()) for item, child in self.get_children())
        )

        return new_dict

    def as_flat_dict(self):
        """Produce a vanilla Python flat dictionnary by going through the whole structure and gathering all
        leaf mappings"""

        return super(NestedMapping, self).as_dict()

    def str(self):
        """Pretty representation of the full nested structure using YAML format"""
        return f"""# {self.__class__.__name__}\n---\n""" + yaml.dump(self.as_dict())
