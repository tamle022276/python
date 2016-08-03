#!/usr/bin/env python
# echob.py - echo command line args backwards
import sys

args = sys.argv[1:]          # list of args

while (args):
    print args[-1],          # last argument
    args = args[:-1]         # shift right
print

##########################################

#    $ echob.py one two three
#    three two one
#
