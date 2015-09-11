#!/usr/bin/env python


class SerfError(Exception):
    pass


class SerfMessageError(SerfError):
    pass


def handle_message(obj, msg):
    if len(msg) != 3:
        raise SerfMessageError('Invalid message len[%s] != 3' % len(msg))
    attr, args, kwargs = msg
    if not isinstance(attr, (str, unicode)):
        raise SerfMessageError(
            'Invalid attr type[%s] not str/unicode' % type(attr))
    if not isinstance(args, (list, tuple)):
        raise SerfMessageError(
            'Invalid args type[%s] not list/tuple' % type(args))
    if not isinstance(args, dict):
        raise SerfMessageError(
            'Invalid kwargs type[%s] not dict' % type(kwargs))
    if not hasattr(obj, attr):
        raise SerfMessageError('Missing attr[%s]' % attr)
    obj.send('state', attr)
    try:
        r = getattr(obj, attr)(*args, **kwargs)
    except Exception as e:
        raise SerfError('Exception processing %s: %s' % (msg, e))
    return attr, args, kwargs, r


class Serf(object):
    def __init__(self, pipe):
        self.pipe = pipe
        self.setup()
        self.run()

    def setup(self):
        pass

    def send(self, attr, *args, **kwargs):
        assert isinstance(attr, (str, unicode))
        self.pipe.send((attr, args, kwargs))

    def error(self, *args, **kwargs):
        self.send('error', args, kwargs)
        return True

    def exit(self):
        self.send('exit')

    def run(self):
        self.send('state', 'wait')
        while True:
            msg = self.pipe.recv()
            try:
                result, attr, args, kwargs = handle_message(self, msg)
                if result is not None:
                    self.send(attr, result)
            except Exception as e:
                if self.error(str(e)):
                    break
                else:
                    continue
            self.send('state', 'wait')
            continue
            if len(msg) != 3:
                if self.error('Invalid message len[%s] != 3' % len(msg)):
                    break
                else:
                    continue
            attr, args, kwargs = self.pipe.recv()
            if not isinstance(attr, (str, unicode)):
                if self.error(
                        'Invalid attr type[%s] not str/unicode' % type(attr)):
                    break
                else:
                    continue
            self.send('state', attr)
            if attr == 'exit':
                self.exit()
                break
            if not hasattr(self, attr):
                if self.error('Missing attr[%s]' % attr):
                    break
                else:
                    continue
            try:
                r = getattr(self, attr)(*args, **kwargs)
            except Exception as e:
                if self.error('Exception processing %s: %s' % (msg, e)):
                    break
                else:
                    continue
            if r is not None:
                self.send(attr, r)
            self.send('state', 'wait')


def run_serf(serf, args=None, kwargs=None):
    if args is None:
        args = ()
    if kwargs is None:
        kwargs = {}
    serf(*args, **kwargs)
