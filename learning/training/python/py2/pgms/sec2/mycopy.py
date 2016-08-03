#!/usr/bin/env python
# mycopy.py - shallow vs. deep copy
import copy

D1 = [{"one" : 1, "two" : 2}]
D2 = D1[:]
D3 = copy.deepcopy(D1)

D1.append(3)
D1[0]["two"] = 22

print "D1 =", D1
print "D2 =", D2
print "D3 =", D3

##############################################
#
#     $ mycopy.py
#     D1 = [{'two': 22, 'one': 1}, 3]
#     D2 = [{'two': 22, 'one': 1}]
#     D3 = [{'two': 2, 'one': 1}]
#
