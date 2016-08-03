#!/usr/bin/env python3
# clockthread2.py - ClockThread class
from threading import Thread
from time import ctime, sleep

# your code here...

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
