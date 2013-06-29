#!/usr/bin/env python

from .io import read, write

__all__ = ['read', 'write']

try:
    import qarg
    hasqarg = True
except ImportError:
    hasqarg = False

if hasqarg:
    from . import plot
    __all__.append('plot')
