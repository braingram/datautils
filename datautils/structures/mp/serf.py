#!/usr/bin/env python

import time


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

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self.send('state', value)
        self._state = value

    def setup(self, *args, **kwargs):
        pass

    def send(self, attr, *args, **kwargs):
        assert isinstance(attr, (str, unicode))
        self.pipe.send((attr, args, kwargs))

    def error(self, *args, **kwargs):
        self.send('error', args, kwargs)
        return True

    def exit(self):
        self.state = 'exit'

    def run(self):
        self.state = 'wait'
        while True:
            msg = self.pipe.recv()
            try:
                attr, args, kwargs = parse_message(self, msg)
                self.state = attr
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
            self.state = 'wait'


class TimedSerf(Serf):
    def __init__(self, pipe):
        Serf.__init__(self, pipe)
        self._log = None

    def set_log(self, fn):
        if self._log is not None:
            self._log.close()
        self._log = open(fn, 'w')

    @Serf.state.setter
    def state(self, value):
        if self._log is not None:
            print value
            self._log.write('%.6f,%s\n' % (time.time(), value))
        Serf.state.fset(self, value)

    def __del__(self):
        if self._log is not None:
            self._log.close()


def run_serf(serf, pipe, args=None, kwargs=None):
    if args is None:
        args = ()
    if kwargs is None:
        kwargs = {}
    s = serf(pipe)
    s.setup(*args, **kwargs)
    s.run()
