#!/usr/bin/env python

import pylab

from . import remap
from .. import listify


def pfunc(required=None, optional=None, auto=True):
    required = [] if required is None else required
    optional = [] if optional is None else optional
    required = listify(required)
    optional = listify(optional)

    def wrapper(function):
        if not hasattr(pylab, function.__name__):
            raise AttributeError(
                "Autocall failed, pylab has no: %s" %
                function.__name__)

        def wrapped(d, mapping, **kwargs):
            assert isinstance(mapping, dict)
            for r in required:
                mapping[r] = mapping.get(r, r)
            mapping_copy = mapping.copy()

            # map d
            if not isinstance(d, dict):
                mapping = remap(d, mapping, asdocs=False)
            else:
                for k in mapping:
                    mapping[k] = d[mapping[k]]

            # make args and kwargs
            args = [mapping.pop(r) for r in required]
            for o in optional:
                if o in mapping:
                    args.append(mapping.pop(o))
            kwargs.update(mapping)

            if auto:
                f = getattr(pylab, function.__name__)
                print args, kwargs
                ar = f(*args, **kwargs)
            else:
                ar = None
            fr = function(d, mapping_copy, *args, **kwargs)
            if ar is None:
                return fr
            if fr is None:
                return ar
            return ar, fr

        wrapped.__doc__ = function.__doc__
        wrapped.__name__ = function.__name__
        return wrapped
    return wrapper


@pfunc(required=('left', 'height'))
def bar(d, m, *args, **kwargs):
    return


@pfunc(required=('bottom', 'width'))
def barh(d, m, *args, **kwargs):
    return


@pfunc(required=('x', 'y'))
def errorbar(d, m, *args, **kwargs):
    return


@pfunc(required='x')
def hist(d, m, *args, **kwargs):
    return


@pfunc(required='x', optional=('y', 'fmt'))
def plot(d, m, *args, **kwargs):
    return


@pfunc(required=('x', 'y'))
def scatter(d, m, *args, **kwargs):
    return


@pfunc(required='x')
def boxplot(d, m, *args, **kwargs):
    return


@pfunc(required='y')
def axhline(d, m, *args, **kwargs):
    return


@pfunc(required='x')
def axvline(d, m, *args, **kwargs):
    return


@pfunc(required=('ymin', 'ymax'))
def axhspan(d, m, *args, **kwargs):
    return


@pfunc(required=('xmin', 'xmax'))
def axvspan(d, m, *args, **kwargs):
    return


@pfunc(required=('x', 'y'), optional='c')
def fill(d, m, *args, **kwargs):
    return


@pfunc(required=('x', 'y1'))
def fill_between(d, m, *args, **kwargs):
    return


@pfunc(required=('y', 'x1'))
def fill_betweenx(d, m, *args, **kwargs):
    return


@pfunc(required=('y', 'xmin', 'xmax'))
def hlines(d, m, *args, **kwargs):
    return


@pfunc(required=('x', 'ymin', 'ymax'))
def vlines(d, m, *args, **kwargs):
    return
