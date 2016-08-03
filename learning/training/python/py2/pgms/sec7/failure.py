#!/usr/bin/env python
# failure.py - raise exception when item not found 

class Failure(Exception): pass

def found(item):
    return False

def searchItem():
    item = "abc"
    if found(item):
        return item
    else:
        raise Failure

try:
    item = searchItem()
except Failure:
    print "item not found"
else:
    print "item found"

##################################################
#
#     $ failure.py
#     item not found
#
