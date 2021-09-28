#!/usr/bin/env python

import warnings

from . import ddict
from . import files
from . import grouping
from . import structures
from . import qfilter

# get some useful functions
from .listify import listify
from .qfilter import qf
from .rmap import remap

__version__ = '1.0.4'
__all__ = [
    'ddict', 'files', 'grouping', 'listify', 'structures', 'qf', 'qfilter',
    'remap']

try:
    from .import mongo
except ImportError as E:
    warnings.warn('datautils.mongo failed to import with: %s' % E)

try:
    from .import np
    from .np import mask_array
    __all__.append('mask_array')
except ImportError as E:
    warnings.warn('datautils.np failed to import with: %s' % E)


try:
    from . import plot
    __all__.append('plot')
except ImportError as E:
    warnings.warn('datautils.plot failed to import with: %s' % E)
