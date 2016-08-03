#!/usr/bin/env python
# propagate.py - propagate raise

def raise1():
    raise ValueError("raise1")

def raise2():
    try:
        raise1()
    except:
        print "propagating"
        raise 

def raiseException(func):
    try:
        func()
    except ValueError as who:
        print "ValueError from %s()" %who

raiseException(raise1)
raiseException(raise2)

##################################################
#
#     $ propagate.py
#     ValueError from raise1()
#     propagating
#     ValueError from raise1()
#
