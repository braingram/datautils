#!/usr/bin/env python

from .io import read, write
from .rmap import remap

__all__ = ['read', 'write', 'remap']

try:
    import matplotlib
    hasmatplotlib = True
except ImportError:
    hasmatplotlib = False

if hasmatplotlib:
    from . import plot
    __all__.append('plot')
else:
    warnings.warn('matplotlib failed to import, skipping datautils.mongo.plot')
