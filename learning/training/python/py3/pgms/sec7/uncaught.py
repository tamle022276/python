#!/usr/bin/env python3
# uncaught.py - uncaught exception

def doSomething():
    L1 = [0, 1, 2]
    print(L1 + "abc")         # generate exception

try:
    doSomething()
except Exception as ex:
    import sys
    print("uncaught: ", sys.exc_info()[0], sys.exc_info()[1])

###################################################
#
#     $ uncaught.py
#     uncaught:  <class 'TypeError'> 
#     can only concatenate list (not "str") to list
#
