#!/usr/bin/env python
# intersect.py - intersect function

def intersect(arg1, arg2):
    common = []
    for arg in arg1:
        if arg in arg2:
            common.append(arg)
    return common

answer = intersect([1, 2, 3, 4], (2, 4, 6, 8))
print answer

#####################################
#
#     $ intersect.py
#     [2, 4]
#
