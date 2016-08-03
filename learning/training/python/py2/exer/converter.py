#!/usr/bin/env python2.6
# converter.py - Fahrenheit and Celsius converter
import sys

arg = sys.argv[1]

# your code here...

##########################################

#    $ converter.py 23c
#    73.4f
#
#    $ converter.py 73.4f
#    23c


if "c" in arg:
    ctemp = int(arg[0:-1])
    ftemp = float(9) / float(5) * ctemp + 32
    print (str(ftemp) + "f")

if "f" in arg:
    ftemp = float(arg[0:-1])
    ctemp = (ftemp-32) * float(5)/ float(9)
    print (str(ctemp) + "c")
