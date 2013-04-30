#!/usr/bin/env python

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
