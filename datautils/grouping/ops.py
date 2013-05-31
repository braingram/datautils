#!/usr/bin/env python

from ..listify import listify


def depth(d, l=0):
    if isinstance(d, dict):
        if not len(d.values()):
            return l
        l += 1
        return max([depth(v, l) for v in d.values()])
    else:
        return l


def combine(d0, d1, r=None):
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
        r[k] = combine(d0.get(k, {}), d1.get(k, {}))
    return r


def drop_levels(groups, lvls):
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
