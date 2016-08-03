#!/usr/bin/env python3
# sales2.py - determine yearly sales, -s, -m options
import sys

nargs = len(sys.argv)
if (nargs == 1 or nargs > 3):
    print("Usage: %s [-sm] month" %sys.argv[0])
    exit(1)

args = sys.argv[1:]

skipFlag = False
if (args[0] == "-s"):
    skipFlag = True
    args = args[1:]

monthFlag = False
if (args[0] == "-m"):
    monthFlag = True
    args = args[1:]

month = args[0]
months = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", 
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")

if (month not in months):
    print("%s: Illegal month or option" %sys.argv[0])
    exit(1)

for m in months:
    if (not skipFlag and not monthFlag):
        print("Processing %s" %m)
        if (m == month): break
    if (skipFlag and m != month): 
        print("Processing %s" %m)
        continue
    if (monthFlag and m == month):
        print("Processing %s" %m)
        break

#####################################################
#
#    $ sales2.py 
#    Usage: ./sales.py [-sm] month
#
#    $ sales2.py Mar
#    Processing Jan
#    Processing Feb
#    Processing Mar
#
#    $ sales2.py -s Mar
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
#    $ sales2.py March
#    ./sales2.py: Illegal month or option
#
#    $ sales2.py -x Mar
#    ./sales2.py: Illegal month or option
#
#    $ sales2.py -m Mar
#    Processing Mar
#
