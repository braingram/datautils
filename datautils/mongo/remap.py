#!/usr/bin/env python
"""
Take a list of mongo documents and remap them
from:
    list of dicts
to:
    dict of lists/values

remapping can contain:
    queries: q
        can be global or local
            global : removes document in source [default]
            local : removes document in destination [not implemented]
    functions: f
        can be many-to-one or many-to-many


simple mapping
    'mongo.key' -> 'dict.key'

transform mapping
    func('mongo.key') -> 'dict.key'

compound mapping [assumes many-to-many]
    query(func('mongo.key')) -> 'dict.key'


Examples
------

remap(docs, {'dest': 'mongo.key'})
# [{'mongo.key': 1}, {'mongo.key': 2}] -> {'dest': [1, 2]}

remap(docs, {'mongo.key': {'k': 'dest', 'f': numpy.mean}})
remap(docs, {'dest': {'mon
# [{'mongo.key': 1}, {'mongo.key': 2}] -> {'dest': 1.5}

remap(docs, {'mongo.key': {'k': 'dest', 'q': {'$lt': 1}}})
# [{'mongo.key': 1}, {'mongo.key': 2}] -> {'dest': [2, ]}

# not supported...
remap(docs, {'mongo.key': {'k': 'dest', 'q': {'$gt': 2}, 'f': lambda x: x * 2})
# [{'mongo.key': 1}, {'mongo.key': 2}] -> {'dest': [4, ]}
"""

from .. import ddict
from .. import qfilter


class MappingError(Exception):
    pass


def parse_mapping(mapping):
    """
    Split the mapping into:
        simple mappings
        queries
        functions
        function/queries

    None of this works because it doesn't take into account that there might
    be multiple mappings for a single mongokey
    """
    ss, qs, fs, fqs = {}, {}, {}, {}, {}
    for k, v in mapping.iteritems():
        if isinstance(v, (str, unicode)):
            ss[k] = v
            continue

        if not isinstance(v, dict):
            raise MappingError("%s must be a dict [key=%s]" % (v, k))
        if 'k' not in v:
            raise MappingError(
                "Mapping value missing key[k] [key=%s, value=%s]" % (k, v))

        if 'f' in v:
            # function
            if 'q' in v:
                raise NotImplementedError("Not yet supported")
                fqs[k] = v
            else:
                fs[k] = v
            continue

        if 'q' in v:
            # query
            # if a query for this key already exists, add to it
            qv = qs.get(k, {})
            qv.update(v['q'])
            qs[k] = qv
            # also add a simple mapping, so filtered items will be saved
            ss[k] = v['k']
            continue

        raise MappingError("Unknown mapping [key=%s, value=%s]" % (k, v))
    return ss, qs, fs, fqs


def apply_functions(docs, fs):
    r = {}
    for (mk, v) in fs.iteritems():
        rk = v['k']
        f = v['f']([d[mk] for d in docs])
    pass


def remap(cursor, mapping):
    docs = [ddict.DDict(d) for d in cursor]
    ss, qs, fs, qfs, fqs = parse_mapping(mapping)
    # first queries
    docs = qfilter.qfilter(docs, qs)

    # then function, queries
    if len(fqs.keys()):
        raise NotImplementedError("function queries are not supported [%s]"
                                  % (fqs.keys(), ))

    # then simple mapping
    rs = [{} for _ in xrange(len(docs))]
    for i in xrange(len(docs)):
        for mk, rk in ss.iteritems():
            rs[i][rk] = docs[i][mk]

    # then functions
    frs = apply_functions(docs, fs)


    pass
