#!/usr/bin/env python
"""
Plot recording locations

- 3d plot
- 2d projections
    - x = ml, y = dv
    - x = ap, y = dv
    - x = ap, y = ct
    - x = ct, y = cr
"""

#import re

import pylab
import pymongo

import qarg

from .. import grouping
from .. import np
from ..plot import mapped


def parse_opts(opts):
    """
    code(foo) : code foo (useful for plotting lists of strings

    -- planned --
    numpy.bar(foo) : call a numpy function on foo
    """
    for k in opts:
        if ':' in opts[k]:
            f, sk = opts[k].split(':')
            f = np.flookup.lookup(f)
            opts[k] = {'k': sk, 'f': f}
    return opts


def plot(args=None, **kwargs):
    """
    Plot documents from a mongo database

    Options
    ------

    args : list of arguments to parse (see qarg.simple.parse)
        when None (default) sys.argv[1:] will be used

    Additional Keyword Arguments
    ------

    save : string or False
        if defined, save the resulting plot to filename=save

    hide : boolean (default = False)
        if False, show the plot

    ptype : string
        plot type, used with getattr(datautils.plot.mapped, ptype)

    host : string
        mongodb host to connect to

    database : string
        mongodb database to query

    collection : string
        mongodb collection to query

    query : dict
        query to issue to collection

    group : string
        group documents by some attribute, then plot each group
        if None (default), do not group
    """
    _, opts = qarg.simple.parse(args)

    save = kwargs.pop('save', False)
    #save = opts.pop('S', save)
    save = opts.pop('save', save)

    hide = kwargs.pop('hide', False)
    #hide = opts.pop('H', hide)
    hide = opts.pop('hide', hide)

    ptype = kwargs.pop('ptype', 'scatter')
    #ptype = opts.pop('T', ptype)
    ptype = opts.pop('ptype', ptype)

    host = kwargs.pop('host', None)
    #host = opts.pop('H', host)
    host = opts.pop('host', host)

    database = kwargs.pop('database', None)
    #database = opts.pop('D', database)
    database = opts.pop('database', database)

    collection = kwargs.pop('collection', None)
    #collection = opts.pop('C', collection)
    collection = opts.pop('collection', collection)

    collection = pymongo.Connection(host)[database][collection]

    query = kwargs.pop('query', {})
    query.update(opts.pop('query', {}))

    groupkey = kwargs.pop('group', None)
    if (groupkey is not None) and (not isinstance(groupkey, (str, unicode))):
        raise ValueError("Grouping can only be done by string: %s" % groupkey)

    opts = parse_opts(opts)
    mask = {}
    for k in opts:
        if isinstance(opts[k], dict):
            mask[opts[k]['k']] = True
        else:
            mask[opts[k]] = True
    if groupkey is not None:
        mask[groupkey] = True

    data = [d for d in collection.find(query, mask)]

    f = getattr(mapped, ptype)

    if groupkey is not None:
        g = grouping.group(data, groupkey)
        ks = sorted(g.keys())
        cm = pylab.cm.get_cmap()
        colors = [cm(float(i) / (len(ks) - 1)) for i in xrange(len(ks))]
        for (c, k) in zip(colors, ks):
            f(g[k], opts, decorate=True, label=k, color=c, **kwargs)
        pylab.legend()
    else:
        f(data, opts, decorate=True, **kwargs)

    if save:
        pylab.savefig(save)

    if not hide:
        pylab.show()
