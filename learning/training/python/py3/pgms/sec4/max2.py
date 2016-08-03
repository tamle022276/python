#!/usr/bin/env python3
# max2.py - find max, better

def max(first, *args):
    for arg in args:
        if (arg > first):
            first = arg
    return first

print(max(22, 63, 43, 18))
print(max("one", "two", "three"))
print(max([1, 1], [3, 3], [2, 2])) 

#####################################
#
#     $ max2.py
#     63
#     two
#     [3, 3]
#
