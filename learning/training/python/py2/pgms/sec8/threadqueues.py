#!/usr/bin/env python
# threadqueues.py - thread queues
from threading import Thread
from Queue import Queue
from logging import basicConfig, debug, DEBUG

basicConfig(level=DEBUG, format="(%(threadName)s) %(message)s",)

sentinel = object()             # like EOF

def producer(myqueue):
    for data in range(5):
        debug("sending %d", data)
        myqueue.put(data)       # write data to queue
    myqueue.put(sentinel)       # no more data

def consumer(myqueue):
    while True:
        data = myqueue.get()    # read data from queue
        if data is sentinel:    # check end of data
            break
        debug("receiving %d", data)

myqueue = Queue()
consumer = Thread(target=consumer, args=(myqueue,))
producer = Thread(target=producer, args=(myqueue,))

debug("starting...")
consumer.start()
producer.start()

##################################################
#
#     $ threadqueues.py
#     (MainThread) starting...
#     (Thread-2) sending 0
#     (Thread-1) receiving 0
#     (Thread-2) sending 1
#     (Thread-1) receiving 1
#     (Thread-2) sending 2
#     (Thread-1) receiving 2
#     (Thread-2) sending 3
#     (Thread-1) receiving 3
#     (Thread-2) sending 4
#     (Thread-1) receiving 4
#
