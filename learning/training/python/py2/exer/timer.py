#!/usr/bin/env python
# timer.py - Clock Exceptions
from ClockException import *
from Clock import Clock

try:
    c1 = Clock(12, 33)
    print "%d:%d" %(c1.getHour(), c1.getMinute())
    c2 =  Clock (12, 73)             # raises exception
except ClockException as ex:
    print "%s: %s" %(ex.__class__.__name__, ex.response())
    
#################################################
#
#    $ timer.py
#    12:33
#    MinuteException: minute 73 not between 0 and 59
#
