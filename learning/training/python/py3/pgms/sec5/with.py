#!/usr/bin/env python3
# with.py - with statement
import sys

if (len(sys.argv) < 2):
    sys.stderr.write("Usage: with.py filename\n")
    exit(1)

myfile = sys.argv[1]

f = open(myfile, "r")
for line in f:
    print("%d: %s" %(len(line), line), end="")
f.close()

with open(myfile, "r") as f:
    for line in f:
        print(line, end="")

###############################################
#
#    $ with.py testfile
#    18: This is line one.
#    18: This is line two.
#    20: This is line three.
#    19: This is line four.
#    This is line one.
#    This is line two.
#    This is line three.
#    This is line four.
#
