#!/usr/bin/env python
# sales.py - determine yearly sales
import sys

nargs = len(sys.argv)
if (nargs == 1 or nargs > 3):
    print "Usage: %s [-s] month" %sys.argv[0]
    exit(1)

# your code here...

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
#    $ sales.py -m Mar
#    Processing Mar
#
