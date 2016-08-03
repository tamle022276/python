#!/usr/bin/env python3
# raise.py - raise exception

def raise1():
    raise ValueError("raise1")

def raise2():
    raise ValueError("raise2")

def raiseException(func):
    try:
        func()
    except ValueError as who:
        print("ValueError from %s()" %who)

raiseException(raise1)
raiseException(raise2)

##################################################
#
#     $ raise.py
#     ValueError from raise1()
#     ValueError from raise2()
#
