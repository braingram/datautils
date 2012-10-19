#!/usr/bin/env python


class Group(object):
    def __init__(self, levels=None):
        self.levels = levels

    def level_names(self):
        if self.levels is None:
            return []
        return [l for l in self.levels.keys()]

    def group(self, values, **kwargs):
        #flkwargs = {} if flkwargs is None else flkwargs
        if self.levels is None:
            self.find_levels(values, **kwargs)
        r = type(self.levels)([(k, []) for k in self.levels.keys()])
        for v in values:
            for n, f in self.levels.iteritems():
                if f(v):
                    r[n].append(v)
                    continue
        return r

    __call__ = group
