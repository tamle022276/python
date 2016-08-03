#!/usr/bin/env python3
# sets.py - set functions
from myfuncs import *

answer1 = intersect([1, 2, 3, 4], (2, 4, 6, 8))
print("intersection is", answer1)

answer2 = union([1, 2, 3, 4], (2, 4, 6, 8))
print("union is", answer2)

answer3 = unique([1, 2, 3, 4, 2, 4, 6, 8])
print("unique is", answer3)

#####################################
#
#     $ sets.py
#     intersection is [2, 4]
#     union is [1, 2, 3, 4, 6, 8]
#     unique is [1, 2, 3, 4, 6, 8]
#
