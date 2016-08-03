#!/usr/bin/env python
# threadlocks.py - thread locks
from threading import Thread, Lock, currentThread, enumerate
from time import sleep
from random import random
from logging import basicConfig, debug, DEBUG

basicConfig(level=DEBUG, format="(%(threadName)s) %(message)s",)

class Counter():
    def __init__(self, start=0):
        self.lock = Lock()
        self.value = start
    def incr(self):
        self.lock.acquire()
        try:
            debug("Acquired lock")
            self.value += 1
        finally:
            self.lock.release()
            debug("Released lock")

class Counter2():
    def __init__(self, start=0):
        self.lock = Lock()
        self.value = start
    def incr(self):
        with self.lock:
            debug("Acquired lock")
            self.value += 1
        debug("Released lock")

def myThread(counter):
    for n in range(2):
        pause = random()
        sleep(pause)
        counter.incr()

counter = Counter()
debug("Counter = %d", counter.value)

for n in range(2):
    thread = Thread(target=myThread, args=(counter,))
    thread.start()

debug("Waiting for counter threads")
mainThread = currentThread()
for thread in enumerate():
    if thread is not mainThread:
        thread.join()
debug("Counter = %d", counter.value)

#################################################
#
#     $ threadlocks.py
#     (MainThread) Counter = 0
#     (MainThread) Waiting for counter threads
#     (Thread-2) Acquired lock
#     (Thread-2) Released lock
#     (Thread-1) Acquired lock
#     (Thread-1) Released lock
#     (Thread-2) Acquired lock
#     (Thread-2) Released lock
#     (Thread-1) Acquired lock
#     (Thread-1) Released lock
#     (MainThread) Counter = 4
#
