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


def rget(d, k, *others):
    """
    recursive get
    """
    if len(others):
        return rget(d[k], *others)
    return d[k]


def rset(d, k, v, *others):
    if len(others):
        if k not in d:
            d[k] = {}
        rset(d[k], others[0], v, *others[1:])
    else:
        d[k] = v


def rdel(d, k, *others):
    if len(others):
        rdel(d[k], *others)
    else:
        del d[k]


def dget(d, k, delimiter='.'):
    """
    dotted get
    """
    return rget(d, *k.split(delimiter))


def dset(d, k, v, delimiter='.'):
    ks = k.split(delimiter)
    rset(d, ks[0], v, *ks[1:])


def ddel(d, k, v, delimiter='.'):
    rdel(d, *k.split(delimiter))


def tget(d, k, default=None, delimiter=None):
    """
    try dotted get
    """
    kwargs = {} if delimiter is None else dict(delimiter=delimiter)
    try:
        return dget(d, k, **kwargs)
    except:
        return default


# ------------------ tests ------------------
def test_rget():
    d = {'a': {'b': {'c': 1}}}
    assert rget(d, 'a', 'b', 'c') == 1


def test_dget():
    d = {'a': {'b': {'c': 1}}}
    assert dget(d, 'a.b.c') == 1
