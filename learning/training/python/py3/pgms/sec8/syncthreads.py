#!/usr/bin/env python3
# syncthreads.py - synchronize threads
from threading import Thread, Condition
from time import sleep
from logging import basicConfig, debug, DEBUG

basicConfig(level=DEBUG, format="(%(threadName)s) %(message)s",)

def producer(cond):
    debug("Starting producer")
    with cond: 
        debug("Writing to resource")
        cond.notifyAll()

def consumer(cond):
    debug("Starting consumer")
    with cond: 
        cond.wait()
        debug("Reading from resource")

condition = Condition()
consumer1 = Thread(target=consumer, args=(condition,))
consumer2 = Thread(target=consumer, args=(condition,))
producer = Thread(target=producer, args=(condition,))

consumer1.start()
sleep(2)
consumer2.start()
sleep(2)
producer.start()

##################################################
#
#     $ syncthreads.py
#     (Thread-1) Starting consumer
#     (Thread-2) Starting consumer
#     (Thread-3) Starting producer
#     (Thread-3) Writing to resource
#     (Thread-1) Reading from resource
#     (Thread-2) Reading from resource
#
