#!/usr/bin/env python3
# threadevents.py - thread events
from threading import Thread, Event
from queue import Queue
from logging import basicConfig, debug, DEBUG

basicConfig(level=DEBUG, format="(%(threadName)s) %(message)s",)

sentinel = object()                      # like EOF

def producer(myqueue):
    for data in range(5):
        debug("sending %d", data)
        event = Event()                  # create event
        myqueue.put((data, event))       # write data, event
        event.wait()                     # wait for consumer
    myqueue.put((sentinel, Event()))     # no more data

def consumer(myqueue):
    while True:
        data, event = myqueue.get()      # read data, event
        if data is sentinel:             # check end of data
            break
        debug("receiving %d", data)
        event.set()                      # notify producer

myqueue = Queue()
consumer = Thread(target=consumer, args=(myqueue,))
producer = Thread(target=producer, args=(myqueue,))

debug("starting...")
consumer.start()
producer.start()

##################################################
#
#     $ threadevents.py
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
