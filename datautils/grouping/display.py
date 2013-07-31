#!/usr/bin/env python


from . import ops


def as_table(g, ks0=None, ks1=None, as_cols=True, nfmt=None, default=None,
             percent=False):
    if default is None:
        default = ''
    if ops.depth(g) != 2:
        raise ValueError(
            "as_table only works for 2 deep groupings: %i" % ops.depth(g))
    # check ks0 ks1
    if ks0 is None:
        ks0 = sorted(ops.all_keys(g, 0))
    else:
        aks0 = ops.all_keys(g, 0)
        if not all([k in aks0 for k in ks0]):
            raise ValueError("Invalid keys: %s" % ks0)
    if ks1 is None:
        ks1 = sorted(ops.all_keys(g, 1))
    else:
        aks1 = ops.all_keys(g, 1)
        if not all([k in aks1 for k in ks1]):
            raise ValueError("Invalid keys: %s" % ks1)
    # transpose?
    if as_cols:
        sf = lambda c, r: g[c][r]
        rs = ks1
        cs = ks0
    else:
        sf = lambda c, r: g[r][c]
        rs = ks0
        cs = ks1
    # get format
    if nfmt is None:
        nfmt = '%g'
    #lvs = ops.leaves(g)
    #if not all(map(lambda l: isinstance(l, (int, float)), lvs)):
    #    raise ValueError(
    #        "as_table only works for grouping with int or float leaves")

    # print header
    for c in cs:
        print "\t%s" % c,
        if percent:
            print "\t%s%%" % c,
    print
    # print values
    for r in rs:
        print "%s" % r,
        for c in cs:
            try:
                s = nfmt % sf(c, r)
            except KeyError:
                s = default
            print "\t%s" % s,
            if percent:
                try:
                    p = sf(c, r) / float(sf(cs[0], r)) * 100.
                    s = '%.0f%%' % p
                except KeyError:
                    s = default
                print "\t%s" % s,
        print
