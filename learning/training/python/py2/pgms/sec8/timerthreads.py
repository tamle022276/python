#!/usr/bin/env python
# timerthreads.py - timer threads
from threading import Timer
from time import sleep
from logging import basicConfig, debug, DEBUG

basicConfig(level=DEBUG, format="(%(threadName)s) %(message)s",)

def myThread():
    debug("myThread running")

thread1 = Timer(3, myThread)
thread1.setName("Thread1")
thread2 = Timer(3, myThread)
thread2.setName("Thread2")

debug("starting timers")
thread1.start()
thread2.start()

debug("waiting before canceling %s", thread2.getName())
sleep(2)
debug("canceling %s", thread2.getName())
thread2.cancel()

print "Main thread is done"

##################################################
#
#     $ timerthreads.py
#     (MainThread) starting timers
#     (MainThread) waiting before canceling Thread2
#     (MainThread) canceling Thread2
#     Main thread is done
#     (Thread1) myThread running
#
