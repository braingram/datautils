mongo query like filtering of list of dicts

Examples
======

see query.test_qfilter

```python

from datautils.qfilter import qf

l = [
    {'a': {'b': {'c': 1}}},
    {'a': {'b': {'c': 2}}},
    {'all': [1, 2, 3]},
]

qf(l, {'a.b.c' 1}) == [{'a': {'b': {'c': 1}}}]
# etc...
```
