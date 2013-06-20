#!/usr/bin/env python
"""
group plotting functions
"""

import matplotlib.patheffects
import numpy
import pylab

from ..grouping import ops


def stat(g, f=None, fmt='%s', imshow_kwargs=None, text_kwargs=None,
         text_effects=None, xticks_kwargs=None, yticks_kwargs=None):
    """Only works with depth == 2 """
    assert ops.depth(g) == 2
    if f is not None:
        s = ops.stat(g, f)
    else:
        s = g
    yks = sorted(s.keys())
    h = len(yks)
    w = -1
    for i in s.values():
        if len(i) > w:
            w = len(i)
            xks = sorted(i.keys())
    assert w != -1

    # make matrix
    n = numpy.empty((h, w))
    n[:, :] = numpy.nan
    for (i0, k0) in enumerate(sorted(s.keys())):
        for (i1, k1) in enumerate(sorted(s[k0].keys())):
            n[i0, i1] = s[k0][k1]

    # make imshow
    if imshow_kwargs is None:
        imshow_kwargs = {'interpolation': 'nearest'}
    else:
        imshow_kwargs['interpolation'] = \
            imshow_kwargs.get('interpolation', 'nearest')
    pylab.imshow(n, **imshow_kwargs)

    # write out stats
    if text_kwargs is None:
        text_kwargs = {'va': 'center', 'ha': 'center'}
    else:
        text_kwargs['va'] = text_kwargs.get('va', 'center')
        text_kwargs['ha'] = text_kwargs.get('ha', 'center')
    if text_effects is None:
        text_effects = [matplotlib.patheffects.withStroke(
            linewidth=3, foreground='w')]
    for i in xrange(n.shape[0]):
        for j in xrange(n.shape[1]):
            if not numpy.isnan(n[i, j]):
                txt = pylab.text(j, i, fmt % n[i, j], **text_kwargs)
                if text_effects is not None:
                    txt.set_path_effects(text_effects)

    # labels
    if xticks_kwargs is None:
        if max([len(str(x)) for x in xks]) > 2:
            xticks_kwargs = {'rotation': 45}
        else:
            xticks_kwargs = {}
    if yticks_kwargs is None:
        yticks_kwargs = {}

    pylab.xticks(range(len(xks)), xks, **xticks_kwargs)
    pylab.yticks(range(len(yks)), yks, **yticks_kwargs)
    return n
