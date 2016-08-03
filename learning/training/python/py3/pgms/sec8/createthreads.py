#!/usr/bin/env python3
# createthreads.py - create threads
from threading import Thread

def myThread():
    print("myThread")

for thread in range(4):
    thread = Thread(target=myThread)
    thread.start()

##################################################
#
#     $ createthreads.py
#     myThread
#     myThread
#     myThread
#     myThread
#
