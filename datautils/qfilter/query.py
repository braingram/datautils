#!/usr/bin/env python
"""
Mongo-like queries on a list of dicts

I have not implemented the full set of mongodb queries [see vtests]
"""

#import collections
import itertools
import math

from ..ddict import dget
from ..listify import listify


def splits(data, key, n):
    data = [d[key] for d in data]
    minv = min(data)
    maxv = max(data) + 1
    delta = (maxv - minv) / float(n)
    s = minv
    qs = []
    for i in range(n):
        e = s + delta
        qs.append({key: {'$gte': s, '$lt': e}})
        s = e
    return qs


def combine(q0, q1, *args):
    """
    Combine queries or lists of queries

    if q0 or q1 is a list, the result will be len(q0) * len(q1) items long
    where the items will be:
        q0[0] + q1[0], q0[0] + q1[1]... q0[0] + q1[-1]... q0[-1] + q1[-1]
    """
    if len(args):
        qs = combine(q0, q1)
        return combine(qs, *args)
    if q0 is None:
        if q1 is None:
            return []
        return listify(q1)
    if q1 is None:
        return listify(q0)
    q0 = listify(q0)
    q1 = listify(q1)
    qs = []
    for i0 in q0:
        for i1 in q1:
            q = {}
            q.update(i0)
            q.update(i1)
            qs.append(q)
    return qs


# ----------- Query Value parsing -----------
def elemMatch_vtest(t):
    test = make_value_test(t)

    def elem_test(value):
        return any([test(v) for v in itertools.chain.from_iterable(value)])
    return elem_test


def not_vtest(t):
    test = make_value_test(t)
    return lambda v: (not test(v))


def nor_vtest(t):
    tests = [make_value_test(i) for i in t]
    return lambda v: not any([t(v) for t in tests])


def or_vtest(t):
    tests = [make_value_test(i) for i in t]
    return lambda v: any([t(v) for t in tests])


def and_vtest(t):
    tests = [make_value_test(i) for i in t]
    return lambda v: all([t(v) for t in tests])


def eq(a, b):
    # special case for nan
    if isinstance(a, float) and math.isnan(a):
        return isinstance(b, float) and math.isnan(b)
    return a == b


def neq(a, b):
    return not eq(a, b)
# for a given test value [t] construct a value test that when run on
# a value [v] returns either True or False indicating if the value
# passed the test
vtests = {
    '$lt': lambda t: lambda v: v < t,
    '$lte': lambda t: lambda v: v <= t,
    '$gt': lambda t: lambda v: v > t,
    '$gte': lambda t: lambda v: v >= t,
    #'$exists': make_exists_test(t, v),  # done elsewhere
    #'$mod': ???
    '$all': lambda t: lambda v: all((ti in v for ti in tuple(t))),
    '$ne': lambda t: lambda v: neq(v, t),
    '$in': lambda t: lambda v: (any((vi in t for vi in v))) \
            if isinstance(v, (tuple, list)) \
            else (v in t),
    '$nin': lambda t: lambda v: (all((vi not in t for vi in v))) \
            if isinstance(v, (tuple, list)) \
            else (v not in t),
    '$nor': nor_vtest,
    '$or': or_vtest,
    '$and': and_vtest,
    #'$size': ???
    #'$type': ???
    #'$elemMatch': ???
    '$elemMatch': elemMatch_vtest,
    '$not': not_vtest
}


def make_value_test(value):
    """
    """
    if not isinstance(value, dict):
        return lambda v: value in v if isinstance(v, (tuple, list)) \
                else eq(v, value)
    # run all value tests, short-circuit on first False
    tests = [vtests[k](v) for k, v in value.items()]
    return lambda v: all((t(v) for t in tests))
# -------------------------------------------


def make_item_test(key, value):
    """
    Parse a query item (key, value pair) and return a function
    """
    # first, check if value has an $exists test
    #test_exists = True
    if isinstance(value, dict) and '$exists' in value:
        value = value.copy()
        if not value['$exists']:  # test for non-existance
            def test_non_existance(i):
                try:
                    dget(i, key)
                except:
                    return True
                return False
            return test_non_existance
            #test_exists = False
        # remove $exists test
        del value['$exists']

    test_value = make_value_test(value)

    def test_item(i):
        try:
            tv = dget(i, key)
        except:
            return False
            #print "Failed to get %s from %s" % (key, i)
            #print "Returning %s" % (not test_exists)
            #return not test_exists
        #if not test_exists:
        #    return False
        #print "Running test_value on %s" % tv
        return test_value(tv)

    return test_item


def make_query_test(query):
    """
    Parse a query dictionary and return a test function
    """
    tests = [make_item_test(k, v) for k, v in query.items()]

    # use a generator function for short-circuitinga
    #print "Query: %s" % query
    #print "Tests: %s" % tests
    return lambda i: all((t(i) for t in tests))


def qfilter(data, query):
    if query == {}:  # short-circuit
        return data
    t = make_query_test(query)
    return [i for i in data if t(i)]


# ------------------ tests ------------------
def test_qfilter():
    items = [
        {'a': {'b': {'c': 1}}},
        {'a': {'b': {'c': 2}}},
        {'all': [1, 2, 3]},
        ]
    # test match
    assert len(qfilter(items, {'a.b.c': 1})) == 1
    assert len(qfilter(items, {'a.b.c': 2})) == 1
    assert len(qfilter(items, {'a.b.c': 3})) == 0
    assert len(qfilter(items, {'a.b.c.d': 1})) == 0
    assert len(qfilter(items, {'d': 1})) == 0
    # exists
    assert len(qfilter(items, {'a.b.c': {'$exists': True}})) == 2
    assert len(qfilter(items, {'a.b.c': {'$exists': False}})) == 1
    # lt
    assert len(qfilter(items, {'a.b.c': {'$lt': 2}})) == 1
    # lte
    assert len(qfilter(items, {'a.b.c': {'$lte': 2}})) == 2
    # gt
    assert len(qfilter(items, {'a.b.c': {'$gt': 1}})) == 1
    # gte
    assert len(qfilter(items, {'a.b.c': {'$gte': 1}})) == 2
    # all
    assert len(qfilter(items, {'all': {'$all': [1, 2]}})) == 1
    assert len(qfilter(items, {'all': {'$all': [1, 2, 3]}})) == 1
    assert len(qfilter(items, {'all': {'$all': [1, 2, 3, 4]}})) == 0
    # ne
    assert len(qfilter(items, {'a.b.c': {'$ne': 1}})) == 1
    assert len(qfilter(items, {'a.b.c': {'$ne': 3}})) == 2
    # in
    assert len(qfilter(items, {'a.b.c': {'$in': [1, 2]}})) == 2
    assert len(qfilter(items, {'a.b.c': {'$in': [1, 2, 3]}})) == 2
    assert len(qfilter(items, {'a.b.c': {'$in': [2, 3]}})) == 1
    assert len(qfilter(items, {'a.b.c': {'$in': [3, 4]}})) == 0
    # --- test with strings --
    assert len(qfilter([{'a': {'b': 'foo'}}], \
            {'a.b': {'$in': ['foo', 'bar']}})) == 1
    # nin
    assert len(qfilter(items, {'a.b.c': {'$nin': [3, 4]}})) == 2
    assert len(qfilter(items, {'a.b.c': {'$nin': [2, 3]}})) == 1
    assert len(qfilter(items, {'a.b.c': {'$nin': [1, 2, 3]}})) == 0
    assert len(qfilter(items, {'a.b.c': {'$nin': [1, 2]}})) == 0

    # nan != nan corner case
    nani = [{'a': 1}, {'a': float('nan')}]
    assert len(qfilter(nani, {'a': float('nan')})) == 1
    assert len(qfilter(nani, {'a': {'$ne': float('nan')}})) == 1


def test():
    test_qfilter()
