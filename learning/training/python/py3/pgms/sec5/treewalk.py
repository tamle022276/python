#!/usr/bin/env python3
# treewalk.py - walk directory tree
import os,sys

# Check command line arguments
if len(sys.argv) == 1:               # if none, use
    topdir = "."                     # use current dir
else:
    topdir = sys.argv[1]             # top directory

for (dirname, sublist, filelist) in os.walk(topdir):
    print("sublist = %s" %sublist)
    print("%s:" %dirname)
    for file in filelist:
        print("\t%s" %file)      

###############################################
#
#    $ treewalk.py mydir
#    sublist = ['subdir1']
#    mydir:
#        alpha
#        base
#    sublist = []
#    mydir/subdir1:
#        number
#        random
