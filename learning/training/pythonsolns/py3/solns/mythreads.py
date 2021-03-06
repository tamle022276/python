#!/usr/bin/env python3
# mythreads.py - spawn threads
from threading import Thread, currentThread
from time import sleep

napTimes = (5, 12, 3, 19, 7)

def birth(number):
    name = currentThread().getName()
    napTime = napTimes[number]
    print("%s sleeping for %d secs" %(name, napTime))
    sleep(napTimes[number])
    print("%s has slept for %d secs" %(name, napTime))

for n in range(5):
    thread = Thread(target=birth, args=(n,))
    thread.start()

##################################################
#
#     $ mythreads.py
#     Thread-1 sleeping for 5 secs
#     Thread-2 sleeping for 12 secs
#     Thread-3 sleeping for 3 secs
#     Thread-4 sleeping for 19 secs
#     Thread-5 sleeping for 7 secs
#     Thread-3 has slept for 3 secs
#     Thread-1 has slept for 5 secs
#     Thread-5 has slept for 7 secs
#     Thread-2 has slept for 12 secs
#     Thread-4 has slept for 19 secs
#
