#!/usr/bin/env python

import logging

from base import Group


def pylinspace(start, end, n):
    d = (end - start) / (n - 1.)
    return [start + d * i for i in xrange(n)]

try:
    import numpy
    minmax = lambda vs: (numpy.min(vs), numpy.max(vs))
    linspace = numpy.linspace
except ImportError, E:
    logging.warning("Failed to import numpy[%s] using slower minmax()" % E)
    minmax = lambda vs: (min(vs), max(vs))
    linspace = numpy.linspace


class ContinuousGroup(Group):
    def find_levels(self, values, key=None, **kwargs):
        self.levels = find_levels(values, key=None, **kwargs)


def right_level_test(start, end):
    def f(v):
        return ((v > start) and (v <= end))
    return f


def left_level_test(start, end):
    def f(v):
        return ((v >= start) and (v < end))
    return f


def both_level_test(start, end):
    def f(v):
        return ((v >= start) and (v <= end))
    return f


def neither_level_test(start, end):
    def f(v):
        return ((v > start) and (v < end))


def level_test(start, end, inclusive):
    if inclusive == 'left':
        return left_level_test(start, end)
    elif inclusive == 'right':
        return right_level_test(start, end)
    elif inclusive == 'both':
        return both_level_test(start, end)
    elif inclusive == 'neither':
        return neither_level_test(start, end)
    else:
        raise ValueError("Invalid inclusive[%s] must be 'right'/'left'" % \
                inclusive)


def name_function(ftype):
    if ftype == 'start':
        return lambda s, e: s
    elif ftype == 'end':
        return lambda s, e: e
    elif ftype == 'middle':
        return lambda s, e: (s + e) / 2.
    elif ftype == 'string':
        return lambda s, e: "(%g, %g)" % (s, e)


def find_levels(values, key=None, n=None, \
        inclusive='histogram', names='start'):
    vs = values if key is None else map(key, values)
    n = len(vs) ** 0.5 if n is None else n
    vmin, vmax = minmax(vs)
    bounds = linspace(vmin, vmax, n + 1)
    to_name = name_function(names)
    if inclusive == 'histogram':
        lvls = {}
        # all but last are half-open
        for (s, e) in zip(bounds[:-2], bounds[1:-1]):
            lvls[to_name(s, e)] = left_level_test(s, e)
        s, e = bounds[-2:]
        lvls[to_name(s, e)] = both_level_test(s, e)
        return lvls
    else:
        return dict([(to_name(s, e), level_test(s, e, inclusive)) \
                for (s, e) in bounds])
