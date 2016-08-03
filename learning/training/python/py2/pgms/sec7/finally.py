#!/usr/bin/env python
# finally.py - try/finally

def readRecord(file):
   print "reading file"
   line = file.readline()
   print line,
   #i = int(line)                     # raises ValueError

def readFile(file):
    try:
        readRecord(file)             # could raise exception
    finally:
        file.close()                 # always close file
        print "file closed"

try:
    file = open("myfile", "r")       # open file for reading
    print "file opened"
    readFile(file)
except Exception as ex:
    print "%s Exception" %ex.__class__.__name__

##############################################
#
#     $ finally.py
#     file opened
#     reading file
#     this is my data
#     file closed
#
