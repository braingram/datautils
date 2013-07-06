#!/usr/bin/env python

import numpy


def void_to_dict(v):
    return dict([(k, v[k]) for k in v.dtype.names])


def code(v):
    """
    Convert a 1d array of values into 'codes'
    """
    a = numpy.asarray(v)
    _, r = numpy.unique(a, False, True)
    return r.reshape(a.shape)
