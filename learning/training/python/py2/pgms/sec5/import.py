#!/usr/bin/env python
# import.py - import statement
import sys

print "You have", len(sys.argv[1:]), "arguments"
for i in sys.argv[1:]:
    print i,
print
print "Python platform:", sys.platform

##############################################
#
#     $ import.py one two three
#     You have 3 arguments
#     one two three
#     Python platform: linux2
#
