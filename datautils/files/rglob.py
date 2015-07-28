#!/usr/bin/env python
"""
glob using regular expressions
"""

import os
import re


def irglob(d, r, with_matches=False):
    """
    Return all files in a directory that match a regular expression.

    if with_matches is True, also return the re.match result:
        [(fn, re.match)...]

    kinda like glob.glob but with a regular expression
    """
    if with_matches:
        for fn in os.listdir(d):
            m = re.search(r, fn)
            if m is not None:
                yield fn, m
    else:
        for fn in os.listdir(d):
            if re.search(r, fn) is not None:
                yield fn


def rglob(d, r, with_matches=False):
    return list(irglob(d, r, with_matches))
