#!/usr/bin/env python3
# seekf.py - seek and modify file 
import sys

if (len(sys.argv) < 4):
    sys.stderr.write("Usage: seekf.py filename color shade\n")
    exit(1)

# your code here...

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
