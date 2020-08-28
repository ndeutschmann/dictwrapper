# Dictionary wrapper library

This Python library implements dictionary-like objects (precisely implementing the `collections.abc.MutableMapping` interface)
with specialized properties. At the moment, two classes are defined:

- `DictWrapper`: is a very simple child of `collections.UserDict`, a dictionary-like object which is easier to subclass.
- `NestedMapping`: a structure to easily navigate the leaves of arborescent structures where dictionaries contain subdictionaries.

## DictWrapper

There is not much to say about the `DictWrapper` class: it inherits from `collections.UserDict` and therefore provides

- an internal dictionary `.data`
- `MutableMapping` methods to access this dictionary: `__getitem__`, `__setitem__`, `__len__`, `__contains__`, `__eq__`, `__ne__`, `keys`, `items`, `values`
- extra methods beyond that interface: `__copy__` and `__copy__`
- The `__repr__` method returns `<classname>(<data.__repr__()>)`

## NestedMapping

The `NestedMapping` class deserves some explanation. A high-level description is that it treats nested structures like a tree and exposes the leaf-level mappings like a flat dictionary. Explicitly, consider the following structure:

```python
from dictwrapper.nested import  NestedMapping

tree = NestedMapping({
    "top leaf": "top leaf label",              # depth 0
    "branch": NestedMapping({                  # depth 0
        "lower leaf": "lower leaf label",      # depth 1
        "lower branch": NestedMapping({        # depth 1
            "lowest leaf": "lowest leaf label" # depth 2 
            })    
        }),
    "other branch": NestedMapping({            # depth 0
        "other leaf": "other leaf label"       # depth 1
    })
})
```

which can be represented as follow
```text
root:               tree___________________
                    /   \                  \
depth 0:    top leaf     branch             other branch         
                        /      \                   |
depth 1:      lower leaf       lower branch      other leaf
                              /
depth 2:           lowest leaf
```

from a user point of view, the object `tree` behaves exactly like the following dictionary:
```python
tree = {
    "top leaf": "top leaf label",              
    "lower leaf": "lower leaf label",
    "lowest leaf": "lowest leaf label",
    "other leaf": "other leaf label"
}
```
values can be accessed, edited or added by subscripting the object with `[]`, iterating over it yields the sequence of
its leaf keys, leaf keys can be checked for membership using the `in` operator, `keys`, `items` and `values` are accessible.

Subscripting on read and write fails when multiple keys match the request. When setting the value assocated to a key,
if this key exists at any level, the corresponding value is replaced. If the key is not found anywhere in the structure,
it is added as a top-level leaf.

The default creation mode is from an object convertible to a dictionary by calling `dict` on it. The class creator method has two optional parameters: `recursive` and `check`, both defaulting to `True`. If `recursive` is `True`, the creator goes through the dictionary structure and converts any sub-dictionary to a `NestedMapping`, otherwise they are left as they are. If `check` is `True`, the creator verifies the structure after instantiation and looks for any repeated keys at any levels and throws an exception if any are found. Since this structure is intended to hold configurations, YAML importation with `pyyaml` is also included using `NestedMapping.from_yaml(yaml_file_path, loader=yaml.Loader, recursive=True, check=True)` and  `NestedMapping.from_yaml_stream(stream, loader=yaml.Loader, recursive=True, check=True)`.

Finally, again with the application to configurations, calling the `.to_dict` method yields a vanilla dictionary that can be passed as function arguments using the `**` operator.

### Why would one use this?

The reason I wrote this is to define manipulate involved configurations with nested parameters passed to attribute
 objects. The main working paradigm is to have a standard working setup defined in some config file with the whole 
 hierarchy of parameters, but being able to easily change some details of the hierarchy during experimentation.
 
For example, let us say a class `ObjectA` has an attribute of class `ObjectB` and that they can both be instantiated
through `ObjectA(paramA1=valueA1, ...., paramAN=valueAN, Bparams={"paramB1": valueB1, ...})` which calls
`ObjectB(**BParams)`, we can then define a default configuration as

```python
DefaultABConfig = NestedConfig({
    "paramA1":valueA1,
    ...
    "paramAN": valueAN,
    "Bparams": {
        "paramB1": value1,
        ...    
}
})
```

And then edit some parameter in `objectB` by calling `DefaultABConfig["paramB12"] = 42`. When several layers are involved and the parameters are transparent enough to
understand which level they belong to, this makes writing and reading scripts easier.
