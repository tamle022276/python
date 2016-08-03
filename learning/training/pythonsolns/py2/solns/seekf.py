#!/usr/bin/env python
# seekf.py - seek and modify file 
import sys

if (len(sys.argv) < 4):
    sys.stderr.write("Usage: seekf.py filename color shade\n")
    exit(1)

file = sys.argv[1]
color = sys.argv[2]
newshade = sys.argv[3]

with open(file, "r+") as f:
    while True:
        line = f.readline()
        if not line: 
            print "%s not found" %color
            break
        (name, shade) = line.split()
        if name == color:
            shade = newshade
            f.seek(-len(line), 1)
            f.write(name + " " + shade + "\n")
            #f.write("%s %s\n" %(name, shade))
            break

###############################################
#
#    $ seekf.py colors yellow 6.6
#
#    $ readf.py colors
#    blue 4.4
#    indigo 2.3
#    yellow 6.6
#    green 3.6
#    violet 4.7
#    orange 1.2
#    red 6.2
#
