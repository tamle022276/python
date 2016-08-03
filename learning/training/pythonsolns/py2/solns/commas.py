#!/usr/bin/env python
# commas.py - encode commas for numbers
import sys

input = sys.argv[1]

if (len(input) < 4 ):
    print input
elif (len(input) < 7 ):
    print "%s,%s" %(input[:-3], input [-3:])
else:
    print "%s,%s,%s" %(input[:-6], input[-6:-3], input[-3:])

##########################################

#    $ commas.py 123
#    123
#    $ commas.py 1234
#    1,234
#    $ commas.py 12345
#    12,345
#    $ commas.py 123456
#    123,456
#    $ commas.py 1234567
#    1,234,567
#    $ commas.py 12345678
#    12,345,678
#    $ commas.py 123456789
#    123,456,789

#
