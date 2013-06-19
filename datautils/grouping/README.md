Grouping tools for lists of dicts (like those returned from mongo queries).

Useful for grouping lists of dicts by some sub-value.

```python
from datautils import grouping

l = [{'a': 1}, {'a': 2}, {'a': 1}, {'a': 2}]
g = grouping.group(l, 'a')

assert g[1] == [{'a': 1}, {'a': 1}]
assert g[2] == [{'a': 2}, {'a': 2}]
```

Outline
======

* base: base grouping class [internal]
* coding: utils for coding groups [internal]
* continuous: continuous range class [internal]
* discrete: discrete range class [internal]
* ops: useful operations on groups
* utils: grouping utilties (including group, groupn...)


Useful functions
------

* group and groupn: general grouping functions
    
    Take some values (list of dicts, or list of values) and group them.

    group only allow grouping for 1 key/value/dimension/etc...
    groupn allows grouping by n ...

    If key(s) are given, than values should be a list of dicts.

    Grouping levels can be provided or auto-calculated.

    gtypes refer to the type of grouping to use (continuous or discrete).
    Continuous looks for values within a range.
    Discrete looks for a particular value

    gkwargs allows passing kwargs onto the group class constructor.
    This is useful for defining the number of levels (gkwargs={'n': 10})
    
* ops.depth: measure the depth of a grouping
* ops.combine
* ops.drop_levels
* ops.collapse
* ops.prune
* ops.pick
* ops.stat
