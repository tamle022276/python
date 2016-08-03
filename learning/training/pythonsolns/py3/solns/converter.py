#!/usr/bin/env python3
# converter.py - Fahrenheit and Celsius converter
import sys

arg = sys.argv[1]
temp = float(arg[:-1])

if arg.endswith("c"):
    ftemp = (9.0 / 5.0) * temp + 32
    print("%gf" %ftemp)

if arg.endswith("f"):
    ctemp = (5.0 / 9.0) * (temp - 32)
    print("%gc" %ctemp)

##########################################

#    $ converter.py 23c
#    73.4f
#
#    $ converter.py 73.4f
#    23c
