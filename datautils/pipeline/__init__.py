#!/usr/bin/env python
"""
General data processing pipeline that works like this:

pipeline = Pipeline(cfg)
pipeline(data)
results = pipeline.result()
if pipeline.valid():
    print "All pipeline results were valid"

Accepts a configuration dict that defines:
    1) functions to be run (with optional args & kwargs)
    2) order of functions
    3) function output 'bounds'
    4) logic if function output falls outside of bounds
"""

import copy
import sys

try:
    import contracts
    has_contracts = True
except:
    has_contracts = False


function = type(lambda: None)


def config_list_to_dict(config):
    """
    Takes an list (or tuple) of function definitions and returns a linear
    pipeline
    """
    raise NotImplementedError


class CheckError(Exception):
    pass


def check_result(r, op):
    if not ('bounds' in op):
        return True
    bounds = op['bounds']
    if isinstance(bounds, function):
        return bounds(r)
    if isinstance(bounds, (tuple, list)):  # min, max
        return ((r >= bounds[0]) and (r <= bounds[1]))
    if isinstance(bounds, (str, unicode)):
        if has_contracts:
            try:
                contracts.check(bounds, r)
                return True
            except contracts.ContractNotRespected:
                return False
        else:
            raise ImportError(
                "import contracts failed, contract found[{}".format(bounds))
    raise CheckError("Unknown bounds type {}, {}".format(type(bounds), bounds))


def lookup_function(name, module=None):
    if '.' not in name:
        if module is None:
            raise LookupError("Failed to find function {}".format(name))
        return getattr(module, name)
    mn, sn = name.rsplit('.', 1)
    if module is None:
        if mn not in sys.modules:
            __import__(mn)
        module = sys.modules[mn]
    else:
        module = getattr(module, mn)
    return lookup_function(sn, module)


def build_op(f, **other):
    if isinstance(f, function):
        op = dict(func=f, name=f.__name__)
    else:
        op = copy.deepcopy(f)
    op.update(other)
    if not isinstance(op['func'], function):
        op['func'] = lookup_function(op['func'])
    return op


def get_priority(f):
    return getattr(f, 'get', lambda k, d: 0)('priority', 0)


class Pipeline(object):
    def __init__(self, config=None):
        if config is not None:
            self.parse_config(config)
        self.results = {}
        self.result = None
        self.valid = True

    def parse_config(self, config):
        # convert config 'dict' or 'list' to a stack
        if not isinstance(config, (list, tuple)):
            self._stack = [build_op(config[k], name=k) for k in sorted(
                config.keys(), key=lambda k: get_priority(config[k]),
                reverse=True)]
        else:
            self._stack = [build_op(f) for f in config]

    def __call__(self, arg):
        if isinstance(self._stack, (list, tuple)):
            r = arg
            self.result = {}
            self.valid = True
            for op in self._stack:
                r = op['func'](r, **op.get('kwargs', {}))
                v = check_result(r, op)
                self.valid = (self.valid and v)
                self.results[op.get('name', op['func'].__name__)] = r
            self.result = r
            return self.result


def test_pipeline():
    c = {
        'a': {
            'func': lambda *args, **kwargs: 'a',
            'priority': 1,
        }
    }
    p = Pipeline(c)
    p('')
    r = p.results
    assert r['a'] == 'a'
    c['a']['func'] = lambda *args, **kwargs: 'b'
    p = Pipeline(c)
    try:
        r = p()
    except Exception:
        pass

    # test a linear pipeline
    def foo(i):
        return 'foo'

    def bar(i):
        return 'bar'
    lc = [foo, bar]
    p = Pipeline(lc)
    p('')
    r = p.results
    assert r['foo'] == 'foo'
    assert r['bar'] == 'bar'

    def combine(a, char=None):
        if char is None:
            char = ''
        return a + char
    c = {
        'a': combine,
        'b': {
            'func': combine,
            'priority': 1,
            'kwargs': {
                'char': 'b',
            },
        },
        'c': {
            'func': combine,
            'priority': 2,
            'kwargs': {
                'char': 'c',
            },
        },
    }
    p = Pipeline(c)
    p('z')
    assert p.result == 'zcb'

    def one(arg):
        return 1

    c = {
        'a': {
            'func': one,
            'bounds': (0, 2),
            },
    }

    p = Pipeline(c)
    p('')
    assert p.valid is True
    c['a']['bounds'] = (1, 2)
    p = Pipeline(c)
    p('')
    assert p.valid is True
    c['a']['bounds'] = (0, 1)
    p = Pipeline(c)
    p('')
    assert p.valid is True
    c['a']['bounds'] = (2, 3)
    p = Pipeline(c)
    p('')
    assert p.valid is False
