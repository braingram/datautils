#!/usr/bin/env python

import multiprocessing

from . import serf


class Lord(object):
    def __init__(self):
        self._state = None
        self.process = None

    def state(self, new_state=None, update=False):
        if new_state is None:
            if update:
                self.update()
            return self._state
        self._state = new_state

    def error(self, *args, **kwargs):
        raise serf.SerfError(*args, **kwargs)

    def send(self, attr, *args, **kwargs):
        assert isinstance(attr, (str, unicode))
        self.pipe.send((attr, args, kwargs))

    def start(self, serf_class, args=None, kwargs=None, wait=True):
        if self.process is not None and self.process.is_alive():
            return
        self.pipe, serf_pipe = multiprocessing.Pipe()
        self.process = multiprocessing.Process(
            target=serf.run_serf, args=(
                serf_class, serf_pipe, args, kwargs))
        self.process.daemon = True
        self.process.start()
        if wait:
            while self.state(update=True) is None:
                self.update()

    def stop(self, wait=True):
        if self.process is None:
            return
        if not self.process.is_alive():
            self.process = None
            return
        self.send('exit')
        if not wait:
            return
        while self.process.is_alive():
            self.update()
        self.process.join()
        self.process = None

    def __del__(self):
        self.stop(wait=True)

    def update(self, timeout=0.001):
        while self.pipe.poll(timeout):
            msg = self.pipe.recv()
            attr, args, kwargs = serf.parse_message(self, msg)
            getattr(self, attr)(*args, **kwargs)
