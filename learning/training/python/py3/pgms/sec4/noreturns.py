#!/usr/bin/env python
# noreturns.py - functions with no returns

def proc(arg):
    print(arg)

a = proc("Starting...")       # doesn't return anything
print(a)

list = [2, 4, 6]
list = list.append(8)         # doesn't return anything
print(list)

#####################################
#
#     $ noreturns.py
#     Starting...
#     None
#     None
