#!/usr/bin/env python
# threadnames.py - thread names
from threading import Thread, currentThread
from time import sleep

def myThread():
    name = currentThread().getName()
    print name, "Start"
    sleep(2)
    print name, "End"

def myService():
    name = currentThread().getName()
    print name, "Start"
    sleep(3)
    print name, "End"

mythread = Thread(name="myThread", target=myThread)
myservice = Thread(name="myService", target=myService)
mythread.start()
myservice.start()

##################################################
#
#     $ threadnames.py
#     myThread Start
#     myService Start
#     myThread End
#     myService End
#
