#!/usr/bin/env python
"""
Python state system made of states and transition conditions

states = functions
transitions = functions that returns functions
"""


function = type(lambda: None)


class StateSystem(object):
    def __init__(self, cfg=None, start=None):
        self.states = {}
        self._start = start
        self._state = None
        self._end = False
        if cfg is not None:
            self.parse(cfg)

    def parse(self, cfg):
        self.states = cfg

    def append(self, state, target=None, start=False):
        self.states[state] = target
        if start:
            self._start = state

    def __iter__(self):
        return self

    def __next__(self):
        if (self._state is None) and (self._end is True):
            self._end = False
            raise StopIteration
        if self._state is None:
            self._state = self._start
        r = self._state()
        t = self.states[self._state]
        if t is None:
            self._state = None
            self._end = True
            return r
        elif isinstance(t, function):
            self._state = t
        elif isinstance(t, dict):
            self._state = None
            self._end = True
            for k in t:
                if k(r):
                    self._state = t[k]
                    self._end = False
                    break
        return r

    def __call__(self, start=None):
        if start is not None:
            self._start = start
        return [i for i in self]


def test():
    def po(s):
        def f():
            print(s)
            return s
        f.__name__ = str(s)
        return f

    af = po('a')
    bf = po('b')
    cf = po('c')
    ss = StateSystem()
    ss.append(af, bf)
    ss.append(bf, cf)
    ss.append(cf)
    ss(af)

    scfg = {
        af: bf,
        bf: cf,
        cf: None,
    }

    ss = StateSystem(scfg, start=af)
    ss()

    print("Combined output")
    print(("".join([c for c in ss])))

    f0 = po(0)
    f1 = po(1)
    f2 = po(2)
    f3 = po(3)
    scfg = {
        f0: {
            lambda r: r > 0: f1,
            lambda r: r <= 0: f2,
        },
        f1: f2,
        f2: {
            lambda r: r == 2: f3,
            lambda r: r != 2: f0,
        },
        f3: {
            lambda r: False: None
        },
    }
    ss = StateSystem(scfg, start=f0)
    ss()

    import time
    t0 = time.time()

    def after_i(i):
        return time.time() - t0 < i

    def wait():
        time.sleep(1)

    # state system that waits for 3 seconds
    scfg = {
        f3: {
            after_i: wait,
        },
        wait: f3,
    }
    ss = StateSystem(scfg, start=f3)
    ss()

if __name__ == '__main__':
    test()
