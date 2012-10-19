#!/usr/bin/env python

from continuous import ContinuousGroup
from discrete import DiscreteGroup

DefaultGroup = DiscreteGroup


def guess_type(values, key):
    # try to guess type of grouping
    return DiscreteGroup
    if key is None:
        t = type(values[0])
    else:
        t = type(key(values[0]))
    if t in (int, str, bool):
        return DiscreteGroup
    elif t in (float, ):
        return ContinuousGroup
    else:
        return DiscreteGroup


def group(values, key=None, levels=None, gtype=None, lkwargs=None):
    """

    values : list, tuple or etc...
        values to group

    key : function or None (default)
        used to 'unlock' the grouping value for each value in values

    levels : dict
        grouping levels, keys=names, values=test functions

    lkwargs : dict
        level kwargs
    """
    vs = [key(v) for v in values] if (values is not None) else values
    gtype = guess_type(vs) if gtype is None else gtype
    g = gtype(levels)
    return g(vs, lkwargs)
