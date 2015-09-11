#!/usr/bin/env python


class SerfError(Exception):
    pass


class SerfMessageError(SerfError):
    pass


def parse_message(obj, msg):
    if len(msg) != 3:
        raise SerfMessageError('Invalid message len[%s] != 3' % len(msg))
    attr, args, kwargs = msg
    if not isinstance(attr, (str, unicode)):
        raise SerfMessageError(
            'Invalid attr type[%s] not str/unicode' % type(attr))
    if not isinstance(args, (list, tuple)):
        raise SerfMessageError(
            'Invalid args type[%s] not list/tuple' % type(args))
    if not isinstance(kwargs, dict):
        raise SerfMessageError(
            'Invalid kwargs type[%s] not dict' % type(kwargs))
    if not hasattr(obj, attr):
        raise SerfMessageError('Missing attr[%s]' % attr)
    return attr, args, kwargs


class Serf(object):
    def __init__(self, pipe):
        self.pipe = pipe

    def setup(self, *args, **kwargs):
        pass

    def send(self, attr, *args, **kwargs):
        assert isinstance(attr, (str, unicode))
        self.pipe.send((attr, args, kwargs))

    def error(self, *args, **kwargs):
        self.send('error', args, kwargs)
        return True

    def exit(self):
        self.send('state', 'exit')

    def run(self):
        self.send('state', 'wait')
        while True:
            msg = self.pipe.recv()
            try:
                attr, args, kwargs = parse_message(self, msg)
                self.send('state', attr)
                result = getattr(self, attr)(*args, **kwargs)
                if attr == 'exit':
                    break
                if result is not None:
                    self.send(attr, result)
            except Exception as e:
                if self.error(str(e)):
                    break
                else:
                    continue
            self.send('state', 'wait')


def run_serf(serf, pipe, args=None, kwargs=None):
    if args is None:
        args = ()
    if kwargs is None:
        kwargs = {}
    s = serf(pipe)
    s.setup(*args, **kwargs)
    s.run()
