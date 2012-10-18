#!/usr/bin/env python


import cPickle as pickle

import numpy
import pymongo
import pymongo.binary

from .. import ddict


def write(d, pchar=','):
    """
    Some 'inspiration' (e.g. liberal copying) from:
        https://github.com/jaberg/hyperopt/blob/master/hyperopt/base.py
        SONify
    """
    if isinstance(d, dict):
        nd = {}
        for k in d.keys():
            nk = str(k)
            nk = nk.replace('.', pchar)
            nd[nk] = write(d[k])
        return nd
    elif isinstance(d, (list, tuple)):
        return type(d)([write(i) for i in d])
    elif isinstance(d, numpy.ndarray):
        if d.dtype.isbuiltin == 0:  # this is a structured array
            # pickle it
            return pymongo.binary.Binary(pickle.dumps(d, protocol=2))
        elif d.dtype.isbuiltin == 1:  # this is built in make it a list
            # should I pickle these too?
            return write(list(d))
        else:  # either 2 (custom) or unknown
            raise TypeError("Invalid numpy.ndarray dtype: %s" % d.dtype)
    elif isinstance(d, numpy.bool_):
        return bool(d)
    elif isinstance(d, numpy.integer):
        return int(d)
    elif isinstance(d, numpy.floating):
        return float(d)
    return d


def read(d, dclass=ddict.DDict):
    """
    By default returns DDicts rather than dicts
    """
    if isinstance(d, dict):
        return dclass([(k, read(v)) for (k, v) in d.iteritems()])
    elif isinstance(d, (list, tuple)):
        return type(d)([read(v) for v in d])
    elif isinstance(d, pymongo.binary.Binary):
        return pickle.loads(d)
    return d
