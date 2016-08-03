#!/usr/bin/env python3
# writef.py - write dictionary to file
import sys

mycolors = { "red" : 6.2,  "blue" : 4.4, "green" : 3.6, "orange" : 1.2, 
           "yellow" : 5.3, "violet" : 4.7, "indigo" : 2.3 }

if (len(sys.argv) < 2):
    sys.stderr.write("Usage: writef.py filename\n")
    exit(1)

file = sys.argv[1]

with open(file, "w") as f:
    for (name, shade) in mycolors.items():
        f.write(name + " " + str(shade) + "\n")
        #f.write("%s %3.1f\n" %(name, shade))

###############################################
#
#    $ writef.py colors
#
#    $ cat colors
#    blue 4.4
#    indigo 2.3
#    yellow 5.3
#    green 3.6
#    violet 4.7
#    orange 1.2
#    red 6.2
#
