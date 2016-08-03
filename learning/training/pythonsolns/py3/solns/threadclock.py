#!/usr/bin/env python3
# threadclock.py - ThreadClock class
import threading, time

class ThreadClock(threading.Thread):
    def __init__(self, duration):
        threading.Thread.__init__(self)
        self.duration = duration

    def run(self):
        for num in range(self.duration):
            print((time.ctime()))
            time.sleep(1)

clock = ThreadClock(5)
clock.start()

##################################################
#
#     $ threadclock.py
#     Tue Apr 19 14:34:22 2016
#     Tue Apr 19 14:34:23 2016
#     Tue Apr 19 14:34:24 2016
#     Tue Apr 19 14:34:25 2016
#     Tue Apr 19 14:34:26 2016
#
