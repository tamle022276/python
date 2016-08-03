#!/usr/bin/env python
# myexfiles.py - File Exceptions
from FileException import *

def raise1():
    raise OpenFileException("myfile")

def raise2():
    raise ReadFileException("myfile")

def raise3():
    raise WriteFileException("myfile")

for func in (raise1, raise2, raise3):
    try:
        func()
    except FileException as ex:
        print "%s: %s" %(ex.__class__.__name__, ex.response())
    
#################################################
#
#    $ myexfiles.py
#    OpenFileException: Can't open myfile
#    ReadFileException: Can't read myfile
#    WriteFileException: Can't write myfile
#
