#!/usr/bin/env python

import time
import os

from .lord import Lord
from .serf import Serf
from .serf import TimedSerf


class SleepySerf(TimedSerf):
    def sleep(self, seconds=1):
        time.sleep(seconds)


def test_sleepy_serf():
    l = Lord()
    print("starting")
    l.start(SleepySerf)
    print("sleep")
    l.send('sleep', 1.)
    for i in range(10):
        print("state", l.state())
        time.sleep(0.1)
    l.send('exit')
    for i in range(10):
        print("state", l.state())
        time.sleep(0.1)
        if l.state() == 'exit':
            break
    print("stopping")
    l.stop()


def test_timed_sleepy_serf():
    l = Lord()
    l.start(SleepySerf)
    l.send('set_log', 'sleep.log')
    l.send('sleep', 1.)
    l.stop()
    with open('sleep.log', 'r') as f:
        for l in f:
            print(l)
    os.remove('sleep.log')
