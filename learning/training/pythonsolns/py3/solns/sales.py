#!/usr/bin/env python3
# sales.py - determine yearly sales, -s option
import sys

nargs = len(sys.argv)
if (nargs == 1 or nargs > 3):
    print("Usage: %s [-s] month" %sys.argv[0])
    exit(1)

args = sys.argv[1:]

skipFlag = False
if (args[0] == "-s"):
    skipFlag = True
    args = args[1:]

month = args[0]
months = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", 
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")

if (month not in months):
    print("%s: Illegal month or option" %sys.argv[0])
    exit(1)

for m in months:
    if (skipFlag and m == month): continue
    print("Processing %s" %m)
    if (m == month): break

#####################################################
#
#    $ sales.py 
#    Usage: ./sales.py [-s] month
#
#    $ sales.py Mar
#    Processing Jan
#    Processing Feb
#    Processing Mar
#
#    $ sales.py -s Mar
#    Processing Jan
#    Processing Feb
#    Processing Apr
#    Processing May
#    Processing Jun
#    Processing Jul
#    Processing Aug
#    Processing Sep
#    Processing Oct
#    Processing Nov
#    Processing Dec
#
#    $ sales.py March
#    ./sales.py: Illegal month or option
#
#    $ sales.py -x Mar
#    ./sales.py: Illegal month or option
#
