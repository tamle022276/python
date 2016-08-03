#!/usr/bin/env python3
# threadobjects.py - thread objects
from threading import Thread
from logging import basicConfig, debug, DEBUG

basicConfig(level=DEBUG, format="(%(threadName)s) %(message)s",)

class MyThreadWithArgs(Thread):
    def __init__(self, args=(), kwargs=None):
        Thread.__init__(self)
        self.args = args
        self.kwargs = kwargs

    def run(self):
        debug("thread args: %s, %s", self.args, self.kwargs)

for n in range(3):
    thread = MyThreadWithArgs(args=(n,n+1), kwargs={"bob" : 12, "sue" : 8})
    thread.start()

##################################################
#
#     $ threadobjects.py
#     (Thread-1) thread args: (0, 1), {'bob': 12, 'sue': 8}
#     (Thread-2) thread args: (1, 2), {'bob': 12, 'sue': 8}
#     (Thread-3) thread args: (2, 3), {'bob': 12, 'sue': 8}
#
