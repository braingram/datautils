#!/usr/bin/env python


class FFPipe(object):
    def __init__(self, filename):
        self._filename = filename

    def write(self, message):
        with open(self._filename, 'w') as f:
            f.write(message + '\n')

    def read(self):
        # TODO cache by modtime
        with open(self._filename, 'r') as f:
            msg = f.readline().strip()
        return msg
