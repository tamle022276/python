#!/usr/bin/env python3
# classtree.py - exception hierarchy
import sys

class Base(Exception): pass
class Derived1(Base): pass
class Derived2(Base): pass

def raise1():
    raise Base

def raise2():
    raise Derived1

def raise3():
    raise Derived2

def raise4():
    raise TypeError

for func in (raise1, raise2, raise3, raise4):
    try:
        func()
    except Base as ex:
        print("caught", ex.__class__.__name__)
    except Exception as ex:
        print("%s Exception" %ex.__class__.__name__)

##################################################
#
#     $ classtree.py
#     caught Base
#     caught Derived1
#     caught Derived2
#     TypeError Exception
#
