#!/usr/bin/env python
"""
Code to lookup useful functions by name
"""

import numpy

from . import convert


def finite(v):
    return numpy.array(v)[numpy.isfinite(v)]


def finitemean(v):
    print finite(v)
    print numpy.mean(finite(v))
    return numpy.mean(finite(v))


def finitestd(v):
    return numpy.std(finite(v))


def stderr(v):
    return finitestd(v) / numpy.sqrt(len(finite(v)))


fs = {
    'code': convert.code,
    'codes': numpy.unique,
    'finite': finite,
    'finitemean': finitemean,
    'finitestd': finitestd,
    'stderr': stderr,
}


class FunctionLookupError(Exception):
    pass


def lookup(n):
    if n in fs:
        return fs[n]
    if hasattr(numpy, n):
        return getattr(numpy, n)
    raise FunctionLookupError
