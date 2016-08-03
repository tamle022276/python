#!/usr/bin/env python3
# fixedrec.py - read fixed length records
import sys

if (len(sys.argv) < 4):
    sys.stderr.write("Usage: fixedrec.py fixedfile len num \n")
    exit(1)

file = sys.argv[1]
len = int(sys.argv[2])
num = int(sys.argv[3])

with open(file, "r") as f:
    f.seek(len *num, 0) 
    line = f.read(len)
    print(line,end="")
f.close()

###############################################
#
#    $ fixedrec.py fixedfile 36 2
#    (222) 555-1234 Jeanette and Scott**
#
#    $ fixedrec.py fixedfile 36 4
#    (362) 868-6328 Susan and Patrick***
#

