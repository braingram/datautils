#!/usr/bin/env python

import numpy


def add_column(arr, name, col, dtype=None):
    arr = numpy.asarray(arr)
    if dtype is None:
        dtype = col.dtype
    ndtype = numpy.dtype(arr.dtype.descr + [(name, dtype)])
    narr = numpy.empty(arr.shape, dtype=ndtype)
    for f in arr.dtype.fields:
        narr[f] = arr[f]
    narr[name] = col
    return narr
