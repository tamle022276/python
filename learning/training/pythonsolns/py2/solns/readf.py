#!/usr/bin/env python
# readf.py - read file into dictionary
import sys

if (len(sys.argv) < 2):
    sys.stderr.write("Usage: readf.py filename\n")
    exit(1)

file = sys.argv[1]
mycolors = {}

with open(file, "r") as f:
    for line in f:
        (name, shade) = line.split()
        mycolors[name] = shade

for (name, shade) in mycolors.items():
    print "%s %s" %(name, shade)

###############################################
#
#    $ readf.py colors
#    blue 4.4
#    indigo 2.3
#    yellow 5.3
#    green 3.6
#    violet 4.7
#    orange 1.2
#    red 6.2
#
