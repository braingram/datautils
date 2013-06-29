#!/usr/bin/env python

import numpy


def void_to_dict(v):
    return dict([(k, v[k]) for k in v.dtype.names])
