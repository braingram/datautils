#!/usr/bin/env python

import numpy

from .. import grouping


class GuessError(Exception):
    pass


def void_to_dict(v):
    return dict([(k, v[k]) for k in v.dtype.names])


def code(v):
    """
    Convert a 1d array of values into 'codes'
    """
    a = numpy.asarray(v)
    _, r = numpy.unique(a, False, True)
    return r.reshape(a.shape)


def guess_type(v):
    if isinstance(v, numpy.ndarray):
        return v.dtype
    if len(v) < 1:
        raise GuessError("Cannot guess type for 0 length array")
    if isinstance(v[0], str):
        return 'S' + str(max(list(map(len, v))))
    if isinstance(v[0], str):
        return 'U' + str(max(list(map(len, v))))
    return type(v[0])


def ordered_labeled_array(*args):
    """
    Construct a 'labeled array' from arguments

    args : tuples
        2 tuple of (column name, values)

    dtypes will be guessed using guess_type (usually using the first value)
    the returned array will have size = to the shortest len(values)
    """
    try:
        dt = [(k, guess_type(v)) for (k, v) in args]
    except GuessError as E:
        raise Exception("Failed to guess type: %s" % E)
    return numpy.array(list(zip(*[v for (_, v) in args])), dtype=dt)


def labeled_array(**kwargs):
    """
    Construct a 'labeled array' from keyword arguments

    kwargs will be sorted (alphabetically by key) and passed
    on to ordered_labeled_array
    """
    return ordered_labeled_array(*[(k, kwargs[k]) for k in sorted(kwargs)])


def grouping_to_array(g, default=None, dtype=None, stat=None, pick=None):
    """
    Convert a grouping to a numpy array

    g : grouping(dict)
        grouping to convert

    default : default=None
        value for cells where no value was found
        if default is None, it will be 'guessed' using the dtype
            dtype = str : default = ''
            dtype = int : default = 0
            dtype = float : default = nan
            else empty values will be random

    dtype : numpy.dtype (default=None)
        if None, will be 'guessed' using guess_type on leaf values

    stat : func (default=None)
        if not None, run grouping.ops.stat on function first
        with optional pick

    pick, see stat

    Returns
    ------
        keys : list of lists of keys
            grouping keys at each levels

        array : numpy.ndarray
            grouping values
    """
    if stat is not None:
        g = grouping.ops.stat(g, stat, pick)
    keys = []
    for di in range(grouping.ops.depth(g)):
        keys.append(sorted(grouping.ops.all_keys(g, di)))
    if dtype is None:
        dtype = guess_type(grouping.ops.leaves(g))
    m = numpy.empty([len(k) for k in keys], dtype=dtype)
    if default is not None:
        m[:] = default
    else:
        if numpy.issubdtype(dtype, int):
            m[:] = 0
        elif numpy.issubdtype(dtype, float):
            m[:] = numpy.nan
        elif numpy.issubdtype(dtype, str):
            m[:] = ''
    for (ks, v) in grouping.ops.walk(g):
        inds = tuple([dk.index(k) for (k, dk) in zip(ks, keys)])
        m[inds] = v
    return keys, m
