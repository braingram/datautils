#!/usr/bin/env python

import matplotlib.pyplot


def line(d, mapping, **kwargs):
    assert isinstance(mapping, dict)
    if len(mapping) == 0:
        mapping = dict(x='x')

    for k in mapping:
        mapping[k] = d[mapping[k]]

    ax = matplotlib.pyplot.gca()
    x = mapping.pop('x')
    if 'fmt' in mapping:
        fmt = mapping.pop('fmt')
        if 'y' in mapping:
            y = mapping.pop('y')
            kwargs.update(mapping)
            ax.plot(x, y, fmt, **kwargs)
        else:
            kwargs.update(mapping)
            ax.plot(x, fmt, **kwargs)
    else:
        if 'y' in mapping:
            y = mapping.pop('y')
            kwargs.update(mapping)
            ax.plot(x, y, **kwargs)
        else:
            kwargs.update(mapping)
            ax.plot(x, **kwargs)
