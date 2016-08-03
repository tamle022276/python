#!/usr/bin/env python
# except.py - except clauses
import sys

try:
    filename = "Myfile"
    file = open(filename)
    line = file.readline()
    i = int(line)
except IOError as ex:
    print "I/O error for %s: %s" %(filename, ex.strerror)
except ValueError:
    print "%s: Could not convert data" %filename

###################################################
#
#     $ except.py
#     I/O error for Myfile: No such file or directory
#
