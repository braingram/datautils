#!/usr/bin/env python
"""
'Dotted' dictionary access (similar to pymongo sub-document addressing)

With a dict d,

d = {'a': {'b': 1}}

Normally, to access 'b's value you would run

d['a']['b']

which can be cumbersome for large document heirarchies.
These utilities are meant to allow for access like this

dget(d, 'a.b')
"""

from ops import dget, dset, ddel


class DDict(dict):
    """
    Allow getting, setting and deleting of nested dictionaries
    like those returned from a MongoDB using a '.' notation.

    Example
    -------
    d = DotAddressed({'a': {'b': {'c': 1}}})
    d['a.b.c']  # 1
    del d['a.b.c']  # {'a': {'b': {}}}
    d['a.b'] = 2  # {'a': {'b': 2}}
    """
    def __getitem__(self, key):
        if '.' not in key:
            return dict.__getitem__(self, key)
        # recursively get
        return dget(self, key)

    def __setitem__(self, key, value):
        if '.' not in key:
            dict.__setitem__(self, key, value)
        else:
            #self[key] = value
            dset(self, key, value)

    def __delitem__(self, key):
        if '.' not in key:
            return dict.__deleteitem__(self, key)
        #del self[key]
        ddel(self, key)
