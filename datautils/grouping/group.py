#!/usr/bin/env python

from continuous import ContinuousGroup
from discrete import DiscreteGroup

DefaultGroup = DiscreteGroup


def guess_type(values, key=None):
    # try to guess type of grouping
    v = values[0] if key is None else key(values[0])
    if isinstance(v, float):
        return ContinuousGroup
    else:
        return DiscreteGroup


def lookup_gtype(gtype):
    if isinstance(gtype, str):
        if gtype == 'discrete':
            return DiscreteGroup
        elif gtype == 'continuous':
            return ContinuousGroup
    elif gtype in (DiscreteGroup, ContinuousGroup):
        return gtype
    raise ValueError("Unknown gtype[%s]" % gtype)


def group(values, key=None, levels=None, gtype=None, gkwargs=None):
    """

    values : list, tuple or etc...
        values to group

    key : function or None (default)
        used to 'unlock' the grouping value for each value in values

    levels : dict
        grouping levels, keys=names, values=test functions

    gtype : str, class or None (default)
        the grouping class or string to lookup class (see lookup_gtype)
        if None, gtype will be guesssed (guess_gtype)

    gkwargs : dict
        group kwargs see gtype.group
    """
#    vs = [key(v) for v in values] if (key is not None) else values
    gtype = guess_type(values, key) if gtype is None else lookup_gtype(gtype)
    g = gtype(levels)
    gkwargs = {} if gkwargs is None else gkwargs
    return g(values, key=key, **gkwargs)
