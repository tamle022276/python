#!/usr/bin/env python
# jointhreads.py - join threads
from threading import Thread, currentThread, enumerate
from random import randint
from time import sleep

def myThread():
    name = currentThread().getName()
    print name,
    pause = randint(1, 5)
    print "sleeping %s" %pause
    sleep(pause)
    print "%s wakeup" %name

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
#     $ jointhreads.py
#     Thread-1 sleeping 2
#     Thread-2 sleeping 4
#     Main thread joining Thread-1
#     Thread-3 sleeping 5
#     Thread-1 wakeup
#     Main thread joining Thread-2
#     Thread-2 wakeup
#     Main thread joining Thread-3
#     Thread-3 wakeup
#     Main thread is done
#
