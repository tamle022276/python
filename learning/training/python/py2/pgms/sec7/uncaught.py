#!/usr/bin/env python
# uncaught.py - uncaught exception

def doSomething():
    L1 = [0, 1, 2]
    print L1 + "abc"          # generate exception

try:
    doSomething()
except:
    import sys
    print "uncaught: ", sys.exc_info()[0], sys.exc_info()[1]

###################################################
#
#     $ uncaught.py
#     uncaught:  <type 'exceptions.TypeError'> 
#     can only concatenate list (not "str") to list
#
