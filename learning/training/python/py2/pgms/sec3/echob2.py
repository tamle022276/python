#!/usr/bin/env python
# echob2.py - echo command line args backwards with pop()
import sys

args = sys.argv[1:]          # list of args

while (args):
    print args.pop(),        # remove from end
print

##########################################

#    $ echob2.py one two three
#    three two one
#
