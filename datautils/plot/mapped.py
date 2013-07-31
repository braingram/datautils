#!/usr/bin/env python

import numpy
import pylab
import mpl_toolkits.mplot3d as mplot3d

from .. import grouping
from .. import listify
from .. import np
from .. import remap


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
        these must be defined in the mapping

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
    shadowkwargs = ['decorate', 'xt', 'xtl', 'yt', 'ytl', 'zt', 'ztl'] if \
        shadowkwargs is None else shadowkwargs
    required = listify(required)
    optional = listify(optional)
    shadowkwargs = listify(shadowkwargs)

    def wrapper(function):
        if auto and not hasattr(pylab, function.__name__):
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

            skwargs = dict([(k, kwargs.pop(k)) for k in shadowkwargs
                            if k in kwargs])

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


def read_key(k):
    if isinstance(k, dict):
        return k['k']
    return k


def decorate(ax, d, m, **kwargs):
    if 'x' in kwargs:
        ax.set_xlabel(read_key(m[kwargs['x']]))
    if 'y' in kwargs:
        ax.set_ylabel(read_key(m[kwargs['y']]))
    if 'z' in kwargs:
        ax.set_zlabel(read_key(m[kwargs['z']]))
    if any([k in ('xt', 'xtl', 'yt', 'ytl', 'zt', 'ztl') for k in m]):
        rm = remap(d, m, asdocs=False)
    else:
        return
    if 'xt' in m:
        ax.set_xticks(rm['xt'])
    if 'xtl' in m:
        ax.set_xticklabels(rm['xtl'])
    if 'yt' in m:
        ax.set_yticks(rm['yt'])
    if 'ytl' in m:
        ax.set_yticklabels(rm['ytl'])
    if 'zt' in m:
        ax.set_zticks(rm['zt'])
    if 'ztl' in m:
        ax.set_zticklabels(rm['ztl'])


@pfunc(required=('left', 'height'))
def bar(d, m, *args, **kwargs):
    if kwargs.get('decorate', False):
        decorate(pylab.gca(), d, m, x='left', y='height')
    return


@pfunc(required=('bottom', 'width'))
def barh(d, m, *args, **kwargs):
    if kwargs.get('decorate', False):
        decorate(pylab.gca(), d, m, x='width', y='bottom')
    return


@pfunc(required=('x'), optional='y', auto=False)
def bin(d, m, *args, **kwargs):
    ax = pylab.gca()
    g = grouping.group(args[0], gtype='d')  # thing to group
    lefts = [i for i in range(len(g))]
    labels = sorted(g.keys())
    if len(args) == 1:
        values = [len(g[k]) for k in labels]
    elif len(args) > 1:  # a y was provided
        stat = np.flookup.lookup(kwargs.get('stat', 'mean'))
        d = np.convert.labeled_array(x=args[0], y=args[1])
        values = []
        for l in labels:
            values.append(stat(d[d['x'] == l]['y']))
    r = ax.bar(lefts, values)
    if kwargs.get('decorate', False):
        decorate(ax, d, m, x='x', y='y')
    # make xticks & xticklabels if they're not defined
    if 'xt' not in m:
        ax.set_xticks([i + 0.5 for i in lefts])
    if 'xtl' not in m:
        ax.set_xticklabels(labels)
    return r


@pfunc(required=('x', 'y'))
def errorbar(d, m, *args, **kwargs):
    if kwargs.get('decorate', False):
        decorate(pylab.gca(), d, m, x='x', y='y')
    return


@pfunc(required='x')
def hist(d, m, *args, **kwargs):
    if kwargs.get('decorate', False):
        decorate(pylab.gca(), d, m, x='x')
    return


@pfunc(required='x', optional=('y', 'fmt'))
def plot(d, m, *args, **kwargs):
    if kwargs.get('decorate', False):
        decorate(pylab.gca(), d, m, x='x', y='y')
    return


@pfunc(required=('x', 'y'))
def scatter(d, m, *args, **kwargs):
    if kwargs.get('decorate', False):
        decorate(pylab.gca(), d, m, x='x', y='y')
    return


@pfunc(required='x')
def boxplot(d, m, *args, **kwargs):
    if kwargs.get('decorate', False):
        decorate(pylab.gca(), d, m, x='x')
    return


@pfunc(required='y')
def axhline(d, m, *args, **kwargs):
    if kwargs.get('decorate', False):
        decorate(pylab.gca(), d, m, y='y')
    return


@pfunc(required='x')
def axvline(d, m, *args, **kwargs):
    if kwargs.get('decorate', False):
        decorate(pylab.gca(), d, m, x='x')
    return


@pfunc(required=('ymin', 'ymax'))
def axhspan(d, m, *args, **kwargs):
    if kwargs.get('decorate', False):
        decorate(pylab.gca(), d, m, y='ymin')
    return


@pfunc(required=('xmin', 'xmax'))
def axvspan(d, m, *args, **kwargs):
    if kwargs.get('decorate', False):
        decorate(pylab.gca(), d, m, x='xmin')
    return


@pfunc(required=('x', 'y'), optional='c')
def fill(d, m, *args, **kwargs):
    if kwargs.get('decorate', False):
        decorate(pylab.gca(), d, m, x='x', y='y')
    return


@pfunc(required=('x', 'y1'))
def fill_between(d, m, *args, **kwargs):
    if kwargs.get('decorate', False):
        decorate(pylab.gca(), d, m, x='x', y='y1')
    return


@pfunc(required=('y', 'x1'))
def fill_betweenx(d, m, *args, **kwargs):
    if kwargs.get('decorate', False):
        decorate(pylab.gca(), d, m, x='x1', y='y')
    return


@pfunc(required=('y', 'xmin', 'xmax'))
def hlines(d, m, *args, **kwargs):
    if kwargs.get('decorate', False):
        decorate(pylab.gca(), d, m, x='xmin', y='y')
    return


@pfunc(required=('x', 'ymin', 'ymax'))
def vlines(d, m, *args, **kwargs):
    if kwargs.get('decorate', False):
        decorate(pylab.gca(), d, m, x='x', y='ymin')
    return


# ======= 3D =======
def get_3d_axes():
    ax = pylab.gca()
    if not isinstance(ax, mplot3d.Axes3D):
        # remove axis from plot
        axg = ax.get_geometry()
        # replace with a 3d projected one
        f = pylab.gcf()
        f.delaxes(ax)
        ax = f.add_subplot(*axg, projection='3d')
    return ax


@pfunc(required=('x', 'y'), optional='z', auto=False)
def plot3d(d, m, *args, **kwargs):
    ax = get_3d_axes()
    d = kwargs.pop('decorate', False)
    r = ax.plot(*args, **kwargs)
    if d:
        decorate(ax, d, m, x='x', y='y', z='z')
    return r


@pfunc(required=('x', 'y'), optional='z', auto=False)
def scatter3d(d, m, *args, **kwargs):
    ax = get_3d_axes()
    d = kwargs.pop('decorate', False)
    r = ax.scatter(*args, **kwargs)
    if d:
        decorate(ax, d, m, x='x', y='y', z='z')
    return r


@pfunc(required=('x', 'y', 'z'), auto=False)
def wireframe3d(d, m, *args, **kwargs):
    ax = get_3d_axes()
    d = kwargs.pop('decorate', False)
    r = ax.plot_wireframe(*args, **kwargs)
    if d:
        decorate(ax, d, m, x='x', y='y', z='z')
    return r


@pfunc(required=('x', 'y', 'z'), auto=False)
def surface3d(d, m, *args, **kwargs):
    ax = get_3d_axes()
    d = kwargs.pop('decorate', False)
    r = ax.plot_surface(*args, **kwargs)
    if d:
        decorate(ax, d, m, x='x', y='y', z='z')
    return r


@pfunc(required=('x', 'y', 'z'), auto=False)
def trisurf3d(d, m, *args, **kwargs):
    ax = get_3d_axes()
    d = kwargs.pop('decorate', False)
    r = ax.plot_trisurf(*args, **kwargs)
    if d:
        decorate(ax, d, m, x='x', y='y', z='z')
    return r


@pfunc(required=('x', 'y', 'z'), auto=False)
def contour3d(d, m, *args, **kwargs):
    ax = get_3d_axes()
    d = kwargs.pop('decorate', False)
    r = ax.contour(*args, **kwargs)
    if d:
        decorate(ax, d, m, x='x', y='y', z='z')
    return r


@pfunc(required=('x', 'y', 'z'), auto=False)
def contourf3d(d, m, *args, **kwargs):
    ax = get_3d_axes()
    d = kwargs.pop('decorate', False)
    r = ax.contourf(*args, **kwargs)
    if d:
        decorate(ax, d, m, x='x', y='y', z='z')
    return r


@pfunc(required='col', auto=False)
def collection3d(d, m, *args, **kwargs):
    ax = get_3d_axes()
    kwargs.pop('decorate', False)
    r = ax.add_collection3d(*args, **kwargs)
    return r


@pfunc(required=('left', 'height'), optional='zs', auto=False)
def bar3d(d, m, *args, **kwargs):
    ax = get_3d_axes()
    d = kwargs.pop('decorate', False)
    r = ax.bar3d(*args, **kwargs)
    if d:
        decorate(ax, d, m, x='left', y='height', z='zs')
    return r


@pfunc(required=('x', 'y', 'z', 's'), auto=False)
def text3d(d, m, *args, **kwargs):
    ax = get_3d_axes()
    d = kwargs.pop('decorate', False)
    r = ax.text3d(*args, **kwargs)
    if d:
        decorate(ax, d, m, x='x', y='y', z='z')
    return r
