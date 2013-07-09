#!/usr/bin/env python

import numpy


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
        return 'S' + str(max(map(len, v)))
    if isinstance(v[0], unicode):
        return 'U' + str(max(map(len, v)))
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
    return numpy.array(zip(*[v for (_, v) in args]), dtype=dt)


def labeled_array(**kwargs):
    """
    Construct a 'labeled array' from keyword arguments

    kwargs will be sorted (alphabetically by key) and passed
    on to ordered_labeled_array
    """
    return ordered_labeled_array(*[(k, kwargs[k]) for k in sorted(kwargs)])
