#!/usr/bin/env python3
# clockthread1.py - clock thread
from threading import Thread
from time import ctime, sleep

def myClock(duration):
    for num in range(duration):
        print(ctime())
        sleep(1)

clock = Thread(target=myClock, args=(5,))
clock.start()

##################################################
#
#     $ clockthread1.py
#     Tue Apr 19 14:34:22 2016
#     Tue Apr 19 14:34:23 2016
#     Tue Apr 19 14:34:24 2016
#     Tue Apr 19 14:34:25 2016
#     Tue Apr 19 14:34:26 2016
#
