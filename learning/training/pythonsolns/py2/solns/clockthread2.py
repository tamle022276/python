#!/usr/bin/env python
# clockthread2.py - ClockThread class
from threading import Thread
from time import ctime, sleep

class ClockThread(Thread):
    def __init__(self, duration):
        Thread.__init__(self)
        self.duration = duration

    def run(self):
        for num in range(self.duration):
            print(ctime())
            sleep(1)

clock = ClockThread(5)
clock.start()

##################################################
#
#     $ clockthread2.py
#     Tue Apr 19 14:34:22 2016
#     Tue Apr 19 14:34:23 2016
#     Tue Apr 19 14:34:24 2016
#     Tue Apr 19 14:34:25 2016
#     Tue Apr 19 14:34:26 2016
#
