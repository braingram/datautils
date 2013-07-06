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

import re

import pylab
import pymongo

import qarg

from .. import np
from ..plot import mapped


def parse_opts(opts):
    """
    code(foo) : code foo (useful for plotting lists of strings

    -- planned --
    numpy.bar(foo) : call a numpy function on foo
    """
    for k in opts:
        # check code(foo)
        m = re.findall('^code\((.*)\)$', opts[k])
        if m:
            opts[k] = {'k': m[0], 'f': np.convert.code}
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
    """
    _, opts = qarg.simple.parse(args)

    save = kwargs.get('save', False)
    #save = opts.pop('S', save)
    save = opts.pop('save', save)

    hide = kwargs.get('hide', False)
    #hide = opts.pop('H', hide)
    hide = opts.pop('hide', hide)

    ptype = kwargs.get('ptype', 'scatter')
    #ptype = opts.pop('T', ptype)
    ptype = opts.pop('ptype', ptype)

    host = kwargs.get('host', None)
    #host = opts.pop('H', host)
    host = opts.pop('host', host)

    database = kwargs.get('database', None)
    #database = opts.pop('D', database)
    database = opts.pop('database', database)

    collection = kwargs.get('collection', None)
    #collection = opts.pop('C', collection)
    collection = opts.pop('collection', collection)

    collection = pymongo.Connection(host)[database][collection]

    opts = parse_opts(opts)
    mask = {}
    for k in opts:
        if isinstance(opts[k], dict):
            mask[opts[k]['k']] = True
        else:
            mask[opts[k]] = True

    data = [d for d in collection.find({}, mask)]

    f = getattr(mapped, ptype)

    f(data, opts, decorate=True)

    if save:
        pylab.savefig(save)

    if not hide:
        pylab.show()
