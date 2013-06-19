#!/usr/bin/env python

from ..listify import listify


def depth(d, l=0):
    """Measure grouping depth [how nested is this dict?]"""
    if isinstance(d, dict):
        if not len(d.values()):
            return l
        l += 1
        return max([depth(v, l) for v in d.values()])
    else:
        return l


def combine(d0, d1, r=None):
    """
    Combine two groupings

    Take two groupings (nested dicts) and combine them so that:
        - sub-dictionaries (dicts at some key) are combined
        - lists of grouped values are extended together
            ([1, 2] + [3, 4] = [1, 2, 3, 4])

    This can be though of as taking two trees and adding
    together all the leaves.
    """
    if d0 is None:
        return d1
    if d1 is None:
        return d0
    if (not isinstance(d0, dict)) or (not isinstance(d1, dict)):
        if isinstance(d1, dict) or isinstance(d1, dict):
            raise ValueError("Dictionaries aren't same depth")
        return listify(d0) + listify(d1)
    if r is None:
        r = {}
    for k in set(d0.keys() + d1.keys()):
        r[k] = combine(d0.get(k, None), d1.get(k, None))
    return r


def drop_levels(groups, lvls):
    """
    Drop grouping levels

    lvls : int or list of ints
        index of levels to drop (0 is root levels: groups.keys())

    Example
    ------
    d = {
        'a': {'1': [1, ], '2': [2, ]},
        'b': {'1': [3, ], '2': [4, ]},
    }
    d0 = drop_levels(d, 0)
    d0 = {
        '1': [1, 3],
        '2': [2, 4],
    }
    """
    lvls = sorted(listify(lvls))
    # no levels supplied
    if len(lvls) == 0:
        return groups

    if not isinstance(groups, dict):
        if len(lvls):
            raise ValueError("Invalid drop_levels levels")
        else:
            raise ValueError("drop_levels only works with dicts")

    r = None
    # drop this level
    if lvls[0] == 0:
        lvls.pop(0)
        dl = [l - 1 for l in lvls]
        for k, v in groups.iteritems():
            r = combine(r, drop_levels(v, dl))
        return r

    # don't drop
    r = {}
    dl = [l - 1 for l in lvls]
    for k, v in groups.iteritems():
        r[k] = drop_levels(v, dl)
    return r


def collapse(groups, spaces):
    """
    Collapse grouping levels

    spaces : int or list of ints
        index of spaces between levels to combine
        (space 0 combines groups.keys() and groups[foo].keys())

    Returned group keys are tuples of the collapsed level keys

    Example
    ------
    d = {
        'a': {'1': [1, ], '2': [2, ]},
        'b': {'1': [3, ], '2': [4, ]},
    }
    d0 = collapse(d, 0)
    d0 = {
        ('a', '1'): [1, ],
        ('a', '2'): [2, ],
        ('b', '1'): [3, ],
        ('b', '2'): [4, ],
    }
    """
    spaces = sorted(listify(spaces))
    # no levels supplied
    if len(spaces) == 0:
        return groups

    if not isinstance(groups, dict):
        if len(spaces):
            raise ValueError("Invalid collapse levels")
        else:
            raise ValueError("collapse only works with dicts")

    assert max(spaces) <= depth(groups)

    r = {}
    # collapse this level
    if spaces[0] == 0:
        spaces.pop(0)
        dl = [l - 1 for l in spaces]
        r = {}
        for k, v in groups.iteritems():
            # TODO check v is dict
            if not isinstance(v, dict):
                raise ValueError("Invalid collapse level")
            for k2, v2 in v.iteritems():
                r[tuple(list(listify(k)) + list(listify(k2)))] = v2
        return collapse(r, dl)

    # don't collapse
    dl = [l - 1 for l in spaces]
    for k, v in groups.iteritems():
        r[k] = collapse(v, dl)
    return r


def prune(gts, *keys):
    """
    Remove keys from leaf items

    keys : vargs
        keys to remove

    Example
    ------
    prune({'a': {'b': [{'a': 1, 'b': 2, 'c': 3}]}}, 'a', 'b') ==
        {'a': {'b': [{'c': 3}]}}
    """
    r = {}
    for k in gts.keys():
        if isinstance(gts[k], dict):
            r[k] = prune(gts[k], *keys)
        elif isinstance(gts[k], (list, tuple)):
            r[k] = [dict([(sk, i[sk]) for sk in i.keys() if sk not in keys])
                    for i in gts[k]]
    return r


def pick(gts, key, default=None):
    """
    Reduce leaf nodes from dicts to single values (leaf.get(key, default))

    key : string
        leaf key used to unlock return values

    default : var [default: None]
        value to use if key is not in leaf.keys()


    Example
    ------
    trim({'a': {'b': [{'a': 1, 'b': 2, 'c': 3}]}}, 'c') ==
        {'a': {'b': [3]}}

    """
    if isinstance(gts, dict):
        r = {}
        for k in gts.keys():
            if isinstance(gts[k], dict):
                r[k] = pick(gts[k], key)
            elif isinstance(gts[k], (list, tuple)):
                r[k] = [i.get(key, default) for i in gts[k]]
        return r
    elif isinstance(gts, (list, tuple)):
        return [i.get(key, default) for i in gts]


def stat(gts, func, pick_key=None):
    """
    Apply some function (func) to each leaf

    func : function
        function to apply at each leaf as func(values)

    pick_key : string [default: None]
        if not None, leaf values will be picked with pick(gts, pick_key)
    """
    if pick_key is not None:
        d = pick(gts, pick_key)
    else:
        d = gts

    r = {}
    for k in d.keys():
        if isinstance(d[k], dict):
            r[k] = stat(d[k], func)
        elif isinstance(d[k], (list, tuple)):
            r[k] = func(d[k])
    return r


def test_stat():
    d = {
        'a': {
            'b': [0, 0, 0, 0],
            'c': [1, 1, 1],
            'd': [2, 2],
        },
    }

    tmd = {'a': {'b': 0, 'c': 1, 'd': 2}}
    tld = {'a': {'b': 4, 'c': 3, 'd': 2}}

    md = stat(d, lambda x: sum(x) / float(len(x)))
    assert md == tmd
    ld = stat(d, lambda x: len(x))
    assert ld == tld


def test_pick():
    d = {
        'a': {'b': [{'a': 1, 'b': 2, 'c': 3}]},
    }
    tpa = {'a': {'b': [1]}}
    tpb = {'a': {'b': [2]}}
    tpd = {'a': {'b': [None]}}

    pa = pick(d, 'a')
    assert pa == tpa
    pb = pick(d, 'b')
    assert pb == tpb
    pd = pick(d, 'd')
    assert pd == tpd


def test_prune():
    d = {
        'a': {'b': [{'a': 1, 'b': 2, 'c': 3}]},
    }
    tpa = {
        'a': {'b': [{'b': 2, 'c': 3}]},
    }
    tpab = {
        'a': {'b': [{'c': 3}]},
    }

    pa = prune(d, 'a')
    assert pa == tpa

    pab = prune(d, 'a', 'b')
    assert pab == tpab


def test_drop_levels():
    d = {
        'a': {'1': [1, ], '2': [2, ]},
        'b': {'1': [3, ], '2': [4, ]},
    }

    d0 = {
        '1': [1, 3],
        '2': [2, 4],
    }

    d1 = {
        'a': [1, 2],
        'b': [3, 4],
    }

    l = [1, 2, 3, 4]

    c0 = drop_levels(d, 0)
    assert c0 == d0

    c1 = drop_levels(d, 1)
    assert c1 == d1

    good = True
    try:
        drop_levels(d, 2)
        good = False
    except Exception:
        good = True
    if not good:
        raise Exception("drop_levels failed to raise an exception")

    c = drop_levels(d, (0, 1))
    assert sorted(c) == sorted(l)


def test_collapse():
    d = {
        'a': {
            '1': {
                'i': [1, ],
                'ii': [2, ]},
            '2': {
                'i': [3, ],
                'ii': [4, ]},
        },
        'b': {
            '1': {
                'i': [5, ],
                'ii': [6, ]},
            '2': {
                'i': [7, ],
                'ii': [8, ]},
        }
    }

    d0 = {
        ('a', '1'): d['a']['1'],
        ('a', '2'): d['a']['2'],
        ('b', '1'): d['b']['1'],
        ('b', '2'): d['b']['2'],
    }

    d1 = {
        'a': {
            ('1', 'i'): d['a']['1']['i'],
            ('1', 'ii'): d['a']['1']['ii'],
            ('2', 'i'): d['a']['2']['i'],
            ('2', 'ii'): d['a']['2']['ii'],
        },
        'b': {
            ('1', 'i'): d['b']['1']['i'],
            ('1', 'ii'): d['b']['1']['ii'],
            ('2', 'i'): d['b']['2']['i'],
            ('2', 'ii'): d['b']['2']['ii'],
        },
    }

    d01 = {
        ('a', '1', 'i'): d['a']['1']['i'],
        ('a', '1', 'ii'): d['a']['1']['ii'],
        ('a', '2', 'i'): d['a']['2']['i'],
        ('a', '2', 'ii'): d['a']['2']['ii'],
        ('b', '1', 'i'): d['b']['1']['i'],
        ('b', '1', 'ii'): d['b']['1']['ii'],
        ('b', '2', 'i'): d['b']['2']['i'],
        ('b', '2', 'ii'): d['b']['2']['ii'],
    }

    assert collapse(d, 0) == d0
    assert collapse(d, 1) == d1
    assert collapse(d, (0, 1)) == d01

    good = True
    try:
        collapse(d, 2)
        good = False
    except Exception:
        good = True
    if not good:
        raise Exception('collapse failed to raise an exception')
