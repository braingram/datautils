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
    if isinstance(k, str):
        return rget(d, *k.split(delimiter))
    return rget(d, k)


def dset(d, k, v, delimiter='.'):
    if isinstance(k, str):
        ks = k.split(delimiter)
        rset(d, ks[0], v, *ks[1:])
    else:
        rset(d, k, v)


def ddel(d, k, delimiter='.'):
    if isinstance(k, str):
        rdel(d, *k.split(delimiter))
    else:
        rdel(d, k)


def tget(d, k, default=None, delimiter=None):
    """
    try dotted get
    """
    kwargs = {} if delimiter is None else dict(delimiter=delimiter)
    try:
        return dget(d, k, **kwargs)
    except:
        return default


def tdget(d, k, default=None):
    return tget(d, k, default, '.')


# ------------------ tests ------------------
def test_rget():
    d = {'a': {'b': {'c': 1}}}
    assert rget(d, 'a', 'b', 'c') == 1


def test_dget():
    d = {'a': {'b': {'c': 1}}}
    assert dget(d, 'a.b.c') == 1
