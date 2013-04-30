#!/usr/bin/env python


import numpy


ops = {
    '>': numpy.greater,
    '>=': numpy.greater_equal,
    '<': numpy.less,
    '<=': numpy.less_equal,
    '==': numpy.equal,
    '!=': numpy.not_equal,
    '!0': numpy.nonzero,
}

combs = {
    '&': numpy.logical_and,
    '|': numpy.logical_or,
    '^': numpy.logical_xor,
}


def isstr(s):
    return isinstance(s, str)


def islist(s):
    return isinstance(s, (tuple, list, numpy.ndarray))


def listify(i, n):
    if not islist(i):
        return [i] * n
    assert len(i) == n, \
        "Attempt to listify list of length %s to length %s" % (len(i), n)
    return i


def resolve_selector(s):
    if islist(s):
        return [resolve_selector(i) for i in s]
    if s is None:
        return lambda a: a
    elif isstr(s):
        return lambda a: a[s]
    return s


def resolve_operator(o):
    if islist(o):
        return [resolve_operator(i) for i in o]
    if isinstance(o, str):
        return ops.get(o, getattr(numpy, o))
    return o


def resolve_combiner(c):
    if islist(c):
        return [resolve_combiner(i) for i in c]
    if isstr(c):
        return combs.get(c, getattr(numpy, 'logical_%s' % c))
    return c


def mask_array(array, conditions, operator, selector=None, combiner='and'):
    """
    Examples:
        # create a mask with True where values == 3
        mask_array(a, 3, 'equal')
        # same as
        a == 3

        # create a mask with True where a['outcome'] == foo
        mask_array(a, 'foo', 'equal', 'outcome')
        # same as
        a['outcome'] == 'foo'

        # create a mask with True where a['outcome'] == 'foo' or == 'bar'...
        mask_array(a, ('foo', 'bar', 'baz'), 'equal', 'outcome', 'or')
        # same as
        logical_or(
            logical_or(a['outcome'] == 'bar', a['outcome'] == 'baz'),
            a['outcome'] == 'foo')

    """
    op = resolve_operator(operator)
    sel = resolve_selector(selector)
    comb = resolve_combiner(combiner)
    if islist(conditions):
        N = len(conditions)
        op = listify(op, N)
        sel = listify(sel, N)
        comb = listify(comb, N)
        if comb[0] == numpy.logical_and:
            m = numpy.ones(array.size, dtype=bool)
        else:
            m = numpy.zeros(array.size, dtype=bool)
        for (cond, o, s, c) in zip(conditions, op, sel, comb):
            #foo = s(array)  # 1.2%
            #bar = o(foo, cond)  # 61.7%
            #m = c(m, bar)  # 29%
            m = c(m, o(s(array), cond))  # all the time
        return m
    assert not islist(op)
    assert not islist(sel)
    return op(sel(array), conditions)


def test_mask_array():
    # aliases
    ma = mask_array
    arr = numpy.array
    s = numpy.sum

    a = arr(range(10))
    assert s(ma(a, 10, 'less')) == 10
    assert s(ma(a, -1, 'greater')) == 10
    assert s(ma(a, 5, 'less')) == 5
    assert s(ma(a, 5, 'greater')) == 4
    assert s(ma(a, 5, 'greater_equal')) == 5
    assert s(ma(a, 5, 'less_equal')) == 6
    assert s(ma(a, 10, numpy.less)) == 10
    assert s(ma(a, -1, numpy.greater)) == 10
    assert s(ma(a, (-1, 10), ('greater', 'less'))) == 10
    assert s(ma(a, (4, 6), ('greater', 'less'))) == 1
    assert s(ma(a, (4, 6), ('greater', 'less'), combiner='or')) == 10
    assert s(ma(a, (4, 6, 3), ('greater', 'less', 'equal'),
                combiner=('and', 'and', 'or'))) == 2
