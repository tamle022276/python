#!/usr/bin/env python
# myfunc.py - function objects

def min(x, y):
    if x < y:
        return x
    else:
        return y

def max(x, y):
    if x > y:
        return x
    else:
        return y


myfunc = min
print myfunc(34, 56)

myfunc = max
print myfunc(34, 56)

#####################################
#
#     $ myfunc.py
#     34
#     56
#
