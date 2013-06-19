Grouping tools for lists of dicts (like those returned from mongo queries).

Useful for grouping lists of dicts by some sub-value.

Many of these grouping functions support dotted-dictionary syntax (see ddict).

It is sometimes helpful to think of these groupings as trees with leaves
as the values being grouped and branches as the links between grouping levels.

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
    Continuous looks for values within a range (assumed for str, int)
    Discrete looks for a particular value (assumed for float)

    gkwargs allows passing kwargs onto the group class constructor.
    This is useful for defining the number of levels (gkwargs={'n': 10})
    
* ops.depth: measure the depth of a grouping
* ops.combine: combine two groupings
* ops.drop_levels: drop (completely remove) a grouping level
* ops.collapse: collapse (combine together) two grouping levels
* ops.prune: remove particular leaf sub values
* ops.pick: turn all dict leaves into values at some key
* ops.stat: compute some function at each leaf


Examples
======

see test functions (several in ops) for more examples

```python
from datautils import grouping

l = [
    {'a': 1, 'b': 1},
    {'a': 1, 'b': 2},
    {'a': 2, 'b': 1},
    {'a': 2, 'b': 2},
]

g = grouping.groupn(l, ('a', 'b'))
g[1][1] == [{'a': 1, 'b': 1}]  # etc...

g = grouping.group(l, 'a', gtype='continuous')
g.keys() == [1.0, 1.5]  # ranges guessed from data

g = grouping.group(l, 'a', gtype='continuous', gkwargs={'n': 4})
g.keys() == [1.0, 1.25, 1.5, 1.75]

g = grouping.groupn(l, ('a', 'b'))
grouping.ops.depth(g) == 2

g2 = grouping.ops.combine(g, g)
g2[1][1] == [{'a': 1, 'b': 1}, {'a': 1, 'b': 1}]  # etc...

g0 = grouping.ops.drop_levels(g, 1)  # drop grouping by 'b'
g0[0] == [{'a': 1, 'b': 1}, {'a': 1, 'b': 2}]

cg = grouping.ops.collapse(g, 0)  # combine 0 & 1 [0th space]
cg.keys() == [(1, 1), (1, 2), (2, 1), (2, 2)]

prg = grouping.ops.prune(g, 'b')
prg[1][1] == [{'a': 1}]

pig = grouping.ops.pick(g, 'a')
pig[1][1] == [1, ]

s = grouping.ops.stat(pig, lambda x: [i + 10 for i in x])
s[1][1] == [11, ]

s = grouping.ops.stat(g, lambda x: [i + 10 for i in x], 'a')  # combined pick & stat
s[1][1] == [11, ]
```
