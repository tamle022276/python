#!/usr/bin/env python3
# minmax.py - comparator arguments

def lessthan(a, b):
    return a < b

def greaterthan(a, b):
    return a > b

def minmax(comparator, *args):
    result = args[0]
    for arg in args[1:]:
        if comparator(arg, result):
            result = arg
    return result

print(minmax(lessthan, 54, 12, 88, 49, 63, 18))
print(minmax(greaterthan, 54, 12, 88, 49, 63, 18))

#####################################
#
#     $ minmax.py
#     12      
#     88
#
