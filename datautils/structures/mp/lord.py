#!/usr/bin/env python

import multiprocessing

from . import serf


class Lord(object):
    def __init__(self, serf, args=None, kwargs=None):
        self.pipe, self.serf_pipe = multiprocessing.Pipe()
        self._state = None
        self.process = None
        self.serf = serf
        self.args = args
        self.kwargs = kwargs

    def state(self, new_state=None, update=True):
        if new_state is None:
            if update:
                self.update()
            return self._state
        self._state = new_state

    def setup_process(self):
        self.process = multiprocessing.Process(
            target=serf.run_serf, args=(
                self.serf, self.serf_pipe, self.args, self.kwargs))
        self.process.daemon = True

    def send(self, attr, *args, **kwargs):
        assert isinstance(attr, (str, unicode))
        self.pipe.send((attr, args, kwargs))

    def start(self):
        if self.process is not None and self.process.is_alive():
            return
        self.setup_process()
        self.process.start()

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
        self.send('exit')

    def update(self, timeout=0.001):
        while self.pipe.poll(timeout):
            msg = self.pipe.recv()
            attr, args, kwargs = serf.parse_message(self, msg)
            getattr(self, attr)(*args, **kwargs)
