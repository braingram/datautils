#!/usr/bin/env python
"""
Top level conditional queries do not work. For example:

{'$and': [...]} will instead look for a $and field in the array
"""

import numpy

from ..listify import listify


def not_vtest(a, v):
    assert isinstance(v, dict)
    assert len(v.keys()) == 1
    op = v.keys()[0]
    val = v[op]
    return numpy.logical_not(value_test(a, op, val))


def and_vtest(a, v):
    assert isinstance(v, (tuple, list))
    m = numpy.ones(a.size, dtype=bool)
    for subq in v:
        m = numpy.logical_and(m, value_test(a, subq, m))
    return m


def or_vtest(a, v):
    assert isinstance(v, (tuple, list))
    m = numpy.zeros(a.size, dtype=bool)
    for subq in v:
        m = numpy.logical_or(m, value_test(a, subq, m))
    return m


def all_vtest(a, v):
    # find doc fields that contain all values[v]
    assert a.ndim > 1
    m = numpy.ones(a.size, dtype=bool)
    for iv in v:
        m = numpy.logical_and(
            m, numpy.any(numpy.in1d(a, [iv, ]).reshape(a.shape), 1))
    return m


vtests = {
    #'$exists':,  # doesn't really make sense
    '$lt': numpy.less,
    '$lte': numpy.less_equal,
    '$gt': numpy.greater,
    '$gte': numpy.greater_equal,
    '$ne': numpy.not_equal,
    '$all': all_vtest,
    # TODO not sure how this behaves for a.ndim > 1
    '$in': lambda a, v: numpy.in1d(a, listify(v)),
    '$nin': lambda a, v: numpy.logical_not(numpy.in1d(a, listify(v))),
    '$not': not_vtest,
    '$and': and_vtest,
    '$or': or_vtest,
    '$nor': lambda a, v: numpy.logical_not(or_vtest(a, v)),

    #'$elemMatch':,
}


def value_test(vs, k, v):
    return vtests[k](vs, v)


def subparse(vs, q, mask):
    for k, v in q.iteritems():
        mask = numpy.logical_and(mask, value_test(vs, k, v))
    return mask


def mask(array, query, mask=None):
    if mask is None:
        mask = numpy.ones(array.size, dtype=bool)
    else:
        if numpy.sum(mask) == 0:  # short circuit
            return mask
    # keys are columns
    for k, v in query.iteritems():
        if isinstance(v, dict):
            mask = subparse(array[k], v, mask)
        else:
            if array[k].ndim > 1:
                mask = numpy.logical_and(numpy.any(
                    numpy.in1d(array[k], [v, ]).reshape(array[k].shape), 1))
            else:
                mask = numpy.logical_and(mask, array[k] == v)
        if numpy.sum(mask) == 0:  # short circuit
            return mask
    return mask


def query_array(array, q):
    return array[mask(array, q)]


def test():
    a = []
    for i in xrange(97, 107):
        a.append((i, float(i), chr(i), (i, i * 2, i * 3)))
    dt = numpy.dtype(
        [('i', 'i4'), ('f', 'f4'), ('s', 'S2'), ('a', 'f4', (3,))])
    a = numpy.array(a, dtype=dt)

    qa = lambda q: query_array(a, q)

    assert qa({'i': 97}).size == 1
    assert qa({'f': 97}).size == 1
    assert qa({'i': 96}).size == 0
    assert qa({'s': 'a'}).size == 1

    assert qa({'i': {'$lt': 98}}).size == 1
    assert qa({'f': {'$lt': 98}}).size == 1
    #assert qa({'s': {'$lt': 98}}).size == 1

    assert qa({'i': {'$gt': 106}}).size == 1
    assert qa({'f': {'$gt': 106}}).size == 1
    #assert qa({'s': {'$gt': 106}}).size == 1

    assert qa({'i': {'$lte': 98}}).size == 2
    assert qa({'f': {'$lte': 98}}).size == 2
    #assert qa({'s': {'$lte': 98}}).size == 2

    assert qa({'i': {'$gte': 106}}).size == 2
    assert qa({'f': {'$gte': 106}}).size == 2
    #assert qa({'s': {'$gte': 106}}).size == 2

    assert qa({'i': {'$ne': 97}}).size == a.size - 1
    assert qa({'f': {'$ne': 97}}).size == a.size - 1
    assert qa({'s': {'$ne': 'a'}}).size == a.size - 1

    #'$all': lambda a, v: numpy.all(numpy.in1d(v, a)),
    assert qa({'a': {'$all': [97, ]}}).size == 1
    assert qa({'a': {'$all': [97, 194]}}).size == 1
    assert qa({'a': {'$all': [97, 195]}}).size == 0

    #'$in': lambda a, v: numpy.any(numpy.in1d(v, a)),
    #'$nin': lambda a, v: numpy.logical_not(numpy.any(numpy.in1d(a, v))),
    #'$not': not_vtest,
    #'$and': and_vtest,
    #'$or': or_vtest,
    #'$nor': lambda a, v: numpy.logical_not(or_vtest(a, v)),
    pass
