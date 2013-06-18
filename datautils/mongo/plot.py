#!/usr/bin/env python

import pylab

from . import remap


def pfunc(required=None, optional=None):
    required = [] if required is None else required
    optional = [] if optional is None else optional

    def wrapper(function):
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

            return function(d, mapping_copy, *args, **kwargs)
            #return function(d, mapping, **kwargs)
        wrapped.__doc__ = function.__doc__
        wrapped.__name__ = function.__name__
        return wrapped
    return wrapper


@pfunc(required=('left', 'height'))
def w_bar(d, mapping, *args, **kwargs):
    print mapping
    ax = pylab.gca()
    return ax.bar(*args, **kwargs)


def bar(d, mapping, **kwargs):
    # bar(left, height, ...)
    assert isinstance(mapping, dict)
    mapping['left'] = mapping.get('left', 'left')
    mapping['height'] = mapping.get('height', 'height')

    if not isinstance(d, dict):
        mapping = remap(d, mapping, asdocs=False)
    else:
        for k in mapping:
            mapping[k] = d[mapping[k]]

    left = mapping.pop('left')
    height = mapping.pop('height')

    kwargs.update(mapping)
    ax = pylab.gca()
    return ax.bar(left, height, **kwargs)


# barh(bottom, width, ...)
# errorbar(x, y, {yerr}, {xerr}, ...)
# hist(x, ...)


def plot(d, mapping, **kwargs):
    assert isinstance(mapping, dict)
    if len(mapping) == 0:
        mapping = dict(x='x')

    if not isinstance(d, dict):
        mapping = remap(d, mapping, asdocs=False)
    else:
        for k in mapping:
            mapping[k] = d[mapping[k]]

    args = [mapping.pop('x'), ]
    if 'y' in mapping:
        args.append(mapping.pop('y'))
    if 'fmt' in mapping:
        args.append(mapping.pop('fmt'))

    ax = pylab.gca()
    kwargs.update(mapping)
    return ax.plot(*args, **kwargs)


def scatter(d, mapping, **kwargs):
    assert isinstance(mapping, dict)
    mapping['x'] = mapping.get('x', 'x')
    mapping['y'] = mapping.get('y', 'y')

    if not isinstance(d, dict):
        mapping = remap(d, mapping, asdocs=False)
    else:
        for k in mapping:
            mapping[k] = d[mapping[k]]

    x = mapping.pop('x')
    y = mapping.pop('y')

    kwargs.update(mapping)
    ax = pylab.gca()
    ax.scatter(x, y, **kwargs)


# boxplot(x, ...)

# axhline(y, ...)
# axvline(x, ...)
# axhspan(ymin, ymax, ...)
# axvspan(xmin, xmax, ...)
# fill(x, y, {c}, ...)
# fill_between(x, y1, {y2}, ...)
# fill_betweenx(y, x1, {x2}, ...)
# hlines(y, xmin, xmax, ...)
# vlines(y, ymin, ymax, ...)
