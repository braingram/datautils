#!/usr/bin/env python


class DiscreteCodec:
    def __init__(self, mapping=None):
        self.mapping = {} if mapping is None else mapping

    def __call__(self, value):
        return self.mapping[value]

    def __repr__(self):
        return "DiscreteCodec[%s]" % self.mapping


class ContinuousCodec:
    def __init__(self, code_range=(0, 1.), value_domain=None, values=None):
        self.code_range = code_range
        self.value_domain = value_domain
        if values is not None:
            self.auto(values)
        else:
            self.build_transfer_function()

    def __call__(self, value):
        raise Exception("Attempt to use incomplete codec: %r" % self)

    def auto(self, values):
        self.value_domain = (min(values), max(values))
        self.build_transfer_function()

    def build_transfer_function(self):
        cm = self.code_range[0]
        cr = self.code_range[1] - cm
        vm = float(self.value_domain[0])
        vr = self.value_domain[1] - vm
        self.__call__ = lambda v: (v - vm) / vr * cr + cm

    def __repr__(self):
        return "ContinuousCodec[values(%g,%g)->codes(%g,%g)]" % \
                (self.value_domain + self.code_range)


def discrete_to_codes_from_codec(values, codec):
    codec = DiscreteCodec(codec) if isinstance(codec, dict) else codec
    return [codec(v) for v in values], codec


def discrete_to_codes_from_auto_codec(values, code_min, code_max):
    return discrete_to_codes_from_auto_sorted_codec( \
            values, code_min, code_max, lambda v: v)


def discrete_to_codes_from_auto_sorted_codec(values, \
        code_min, code_max, sort_codec):
    codec = {}
    for v in values:
        codec[v] = 1
    # code range / value range
    m = (code_max - code_min) / (len(codec.keys()) - 1)
    for (i, k) in enumerate(sort_codec(codec.keys())):
        codec[k] = (i * m) + code_min
    return discrete_to_codes_from_codec(values, codec)


def discrete_to_codes(values, code_min=0., code_max=1., \
        codec=None, sort_codec=None):
    if (codec is not None):
        return discrete_to_codes_from_codec(values, codec)
    if (sort_codec is None) or (sort_codec == False):
        return discrete_to_codes_from_auto_codec(values, code_min, code_max)
    sort_codec = sorted if sort_codec == True else sort_codec
    return discrete_to_codes_from_auto_sorted_codec(values, \
            code_min, code_max, sort_codec)


def continuous_to_codes(values, code_min, code_max, codec):
    cc = ContinuousCodec((code_min, code_max), values=values)
    return [cc(v) for v in values], cc


def to_codes(values, type='auto', min=0., max=1., codec=None, \
        sort_codec=True, return_codec=False):
    if not len(values):
        return [], None
    if type == 'auto':
        type = 'continuous' if isinstance(values[0], float) else 'discrete'
    if type == 'continuous':
        codes, codec = continuous_to_codes(values, min, max, codec)
    else:
        codes, codec = discrete_to_codes(values, min, max, codec, sort_codec)
    if return_codec:
        return codes, codec
    return codes
