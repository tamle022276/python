#!/usr/bin/env python3
# outputparams.py - simulate output parameters

def assign(m, n):
    m = 10
    n = [3, 4]
    return m, n

a = 5; b = [1, 2]
(a, b) = assign(a, b)            # updates a, b
print(a, b)

#####################################
#
#     $ outputparams.py
#     10 [3, 4]
#
