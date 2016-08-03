#!/usr/bin/env python
# loggingthreads.py - logging threads
from threading import Thread, currentThread, enumerate
from random import randint
from time import sleep
from logging import basicConfig, debug, DEBUG

basicConfig(level=DEBUG, format="(%(threadName)s) %(message)s",)

def myThread():
    pause = randint(1, 5)
    debug("sleeping %s" %pause)
    sleep(pause)
    debug("wakeup")

for i in range(3):
    mythread = Thread(target=myThread)
    mythread.start()

mainThread = currentThread()
for thread in enumerate():
    if thread is mainThread:
        continue
    print "Main thread joining %s" %thread.getName()
    thread.join()
print "Main thread is done"

##################################################
#
#     $ loggingthreads.py
#     (Thread-1) sleeping 3
#     (Thread-2) sleeping 2
#     Main thread joining Thread-1
#     (Thread-3) sleeping 5
#     (Thread-2) wakeup
#     (Thread-1) wakeup
#     Main thread joining Thread-2
#     Main thread joining Thread-3
#     (Thread-3) wakeup
#     Main thread is done
#
