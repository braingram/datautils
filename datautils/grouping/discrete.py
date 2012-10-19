#!/usr/bin/env python

import logging

from base import Group


def pyunique(values):
    r = {}
    for v in values:
        r[v] = 1
    return r.keys()


try:
    import numpy
    unique = numpy.unique
except ImportError, E:
    logging.warning("Failed to import numpy[%s] defining unique()" % E)
    unique = pyunique


class DiscreteGroup(Group):
    def find_levels(self, values, **kwargs):
        self.levels = find_levels(values, **kwargs)


def level_test(name):
    def f(v):
        return v == name
    return f


def find_levels(values, **kwargs):
    ns = unique(values)
    try:
        ns.sort()
    except:
        pass
    return dict([(n, level_test(n)) for n in ns])
