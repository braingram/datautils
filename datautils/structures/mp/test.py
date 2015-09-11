#!/usr/bin/env python

import time

from .lord import Lord
from .serf import Serf


class SleepySerf(Serf):
    def sleep(self, seconds=1):
        time.sleep(seconds)


def test_sleepy_serf():
    l = Lord()
    print "starting"
    l.start(SleepySerf)
    print "sleep"
    l.send('sleep', 1.)
    for i in xrange(10):
        print "state", l.state()
        time.sleep(0.1)
    l.send('exit')
    for i in xrange(10):
        print "state", l.state()
        time.sleep(0.1)
        if l.state() == 'exit':
            break
    print "stopping"
    l.stop()
