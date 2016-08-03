#!/usr/bin/env python3
# mytuple.py - lists and tuples

mytuple = (45,23,101,[66,12,33],17,29)

T1 = mytuple[:3]
T2 = tuple(mytuple[3])
T3 = mytuple[4:]

L1 = list(T1 + T2 + T3)
L1.sort()
mytuple = tuple(L1)
print(mytuple)

##########################################

#    $ mytuple.py
#    (12, 17, 23, 29, 33, 45, 66, 101)
