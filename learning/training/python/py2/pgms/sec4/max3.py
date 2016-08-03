#!/usr/bin/env python
# max3.py - find max, faster

def max(*args):
    result = list(args)
    result.sort()
    return result[-1]

print max(22, 63, 43, 18)
print max("one", "two", "three")
print max([1, 1], [3, 3], [2, 2]) 

#####################################
#
#     $ max3.py
#     63
#     two
#     [3, 3]
#
