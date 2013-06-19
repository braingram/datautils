#!/usr/bin/env python
"""
Take an item, make it into a list.

I the item is already 'listy' then just return the item.
If not, return the item as a list [of n length]

This module will try to import numpy (numpy.ndarray is listy)
but will continue, without numpy support, if the import fails.

Examples
------

listify(1) == [1, ]
listify(1, n=2) == [1, 1]
listify([1, ]) == [1, ]
listify('a') == ['a', ]
"""

try:
    import numpy
    has_numpy = True
except ImportError:
    has_numpy = False


if has_numpy:
    def is_list(i):
        return isinstance(i, (tuple, list, numpy.ndarray))
else:
    def is_list(i):
        return isinstance(i, (tuple, list))


def listify(i, n=None):
    if is_list(i):
        if (n is not None) and (len(i) != n):
            raise ValueError(
                "Attempt to listify item of length %s to length %" %
                (len(i), n))
        return i
    n = 1 if n is None else n
    return [i] * n
