#!/usr/bin/env python


from . import ops

try:
    from scipy.stats import chisquare as chisquare_test
except ImportError:
    chisquare_test = None


def as_table(g, ks0=None, ks1=None, as_cols=True, nfmt=None, default=None,
             percent=False, chisquare=False):
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
    if chisquare:
        if chisquare_test is None:
            raise ImportError("Cannot import scipy.stats to run chisquare")
        chis = {}  # keys = cols
        chips = {}  # keys = cols
        ns = [float(sf(cs[0], r)) for r in rs]
        for c in cs:
            vs = [sf(c, r) / n for (r, n) in zip(rs, ns)]
            chis[c], chips[c] = chisquare_test(vs)

    # print header
    for c in cs:
        print("\t%s" % c, end=' ')
        if percent:
            print("\t%s%%" % c, end=' ')
    print()
    # print values
    for r in rs:
        print("%s" % r, end=' ')
        for c in cs:
            try:
                s = nfmt % sf(c, r)
            except KeyError:
                s = default
            if chisquare and (chips[c] < 0.05):
                print("\t%s*" % s, end=' ')
            else:
                print("\t%s" % s, end=' ')
            if percent:
                try:
                    p = sf(c, r) / float(sf(cs[0], r)) * 100.
                    s = '%.0f%%' % p
                except KeyError:
                    s = default
                print("\t%s" % s, end=' ')
        print()

    if chisquare:
        print("-------- chisquare results -------")
        print("chi", end=' ')
        for c in cs:
            print("\t%.2f" % (chis[c], ), end=' ')
            if percent:
                print("\t", end=' ')
        print()
        print("chi p", end=' ')
        for c in cs:
            print("\t%.3f" % (chips[c], ), end=' ')
            if percent:
                print("\t", end=' ')
        print()
