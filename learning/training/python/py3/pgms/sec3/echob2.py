#!/usr/bin/env python3
# echob2.py - echo command line args backwards with pop()
import sys

args = sys.argv[1:]                 # list of args

while (args):
    print(args.pop(), end = " ")    # remove from end
print()

##########################################

#    $ echob2.py one two three
#    three two one
#
