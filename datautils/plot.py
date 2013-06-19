#!/usr/bin/env python

import pylab

from . import remap
from . import listify


def pfunc(required=None, optional=None, auto=True, shadowkwargs=None):
    """
    Wrap a plotting function to allow for data parsing and mapping.
    The wrapped functions must accept the following arguments:
        wrapped(data, mapping, *args, **kwargs)

    Where...
        data : data to be plotted, list of dicts, or dict

        mapping : mapping dictionary [see remap]

        *args : variable arguments parsed from data [see required and optional]

        **kwargs : keyword arguments parsed from data and from
            the function call


    Decorator kwargs
    ------

    required : list (or single name)
        required non-keyword arguments to wrapped function

    optional : list (or single name)
        optional non-keyword arguments to wrapped function

    auto : bool [default = True]
        auto call function by using the name of the wrapped function
            getattr(pylab, function.__name__)

    shadowkwargs : list (or single name)
        do not pass on these kwargs to the auto called function


    Examples
    ------

    # auto call example
    @pfunc(required='x', optional=('y', 'fmt'))
    def plot(d, m, *args, **kwargs):
        # pylab.plot(*args, **kwargs) will be auto called
        return

    # shadowkwargs example
    @pfunc(required='x', shadowkwargs='blah')
    def plot(d, m, *args, **kwargs):
        # pylab.plot(*args, **kwargs) will be called without kwargs['blah']
        assert 'blah' in kwargs
        # However, this function can have a kwargs['blah']
    """
    required = [] if required is None else required
    optional = [] if optional is None else optional
    shadowkwargs = [] if shadowkwargs is None else shadowkwargs
    required = listify(required)
    optional = listify(optional)
    shadowkwargs = listify(shadowkwargs)

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

            skwargs = dict([(k, kwargs.pop(k)) for k in shadowkwargs])

            if auto:
                f = getattr(pylab, function.__name__)
                ar = f(*args, **kwargs)
            else:
                ar = None

            kwargs.update(skwargs)
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

# TODO 3D
