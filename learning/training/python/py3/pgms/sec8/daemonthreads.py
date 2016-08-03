#!/usr/bin/env python3
# daemonthreads.py - daemond threads
from threading import Thread
from time import ctime, sleep

def myClock():
    while (True):
        print((ctime()))
        sleep(1)

clock = Thread(target=myClock)
clock.setDaemon(True)   # daemon clock thread

clock.start()           # start daemon running

sleep(5)                # stop clock after 5 secs

##################################################
#
#     $ daemonthreads.py
#     Tue Apr 19 14:34:22 2016
#     Tue Apr 19 14:34:23 2016
#     Tue Apr 19 14:34:24 2016
#     Tue Apr 19 14:34:25 2016
#     Tue Apr 19 14:34:26 2016
#
