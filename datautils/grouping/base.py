#!/usr/bin/env python


class Group(object):
    def __init__(self, levels=None):
        self.levels = levels

    def level_names(self):
        if self.levels is None:
            return []
        return [l for l in self.levels.keys()]

    def group(self, values, key=None, **kwargs):
        #flkwargs = {} if flkwargs is None else flkwargs
        if self.levels is None:
            self.find_levels(values, key=key, **kwargs)
        r = type(self.levels)([(k, []) for k in self.levels.keys()])
        # TODO fix key
        for v in values:
            tv = v if key is None else key(v)
            for n, f in self.levels.iteritems():
                if f(tv):
                    r[n].append(v)
                    continue
        return r

    __call__ = group
