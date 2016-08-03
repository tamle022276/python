#!/usr/bin/env python3
# sets.py - intersect and union functions

def intersect(*args):
    result = []
    for arg in args[0]:
        for other in args[1:]:
            if arg not in other: break
        else:
            result.append(arg)
    return result

def union(*args):
    result = []
    for seq in args:
        for item in seq:
            if item not in result:
                result.append(item)
    return result

print(intersect([1, 2, 3, 4], (2, 4, 6, 8), [2, 4]))
print(union([1, 2, 3, 4], (2, 4, 6, 8), [3, 9]))

#####################################
#
#     $ sets.py
#     [2, 4]
#     [1, 2, 3, 4, 6, 8, 9]
#
