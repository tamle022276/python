#!/usr/bin/env python3
# exbreak.py - break loop

for i in range(3):
    for j in range(3):
        if (i + j == 3):
            break
print(i, j)

##################################################
#
#     $ exbreak.py
#     2 1
#
