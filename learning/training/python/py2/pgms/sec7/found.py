#!/usr/bin/env python
# found.py - raise exception when match found 

class Found(Exception): pass

def found(item):
    if (item == "abc"):
        return True

def searchItem(item):
    if found(item):
        raise Found
    else:
        return

try:
    searchItem("abc")
except Found:
    print "item found"
else:
    print "item not found"

##################################################
#
#     $ found.py
#     item found
#
