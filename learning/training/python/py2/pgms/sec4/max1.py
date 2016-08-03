#!/usr/bin/env python
# max1.py - find max, slow

def max(*args):
    maxval = args[0]
    for arg in args[1:]:
        if (arg > maxval):
            maxval = arg
    return maxval

print max(22, 63, 43, 18)
print max("one", "two", "three")
print max([1, 1], [3, 3], [2, 2]) 

#####################################
#
#     $ max1.py
#     63
#     two
#     [3, 3]
#
