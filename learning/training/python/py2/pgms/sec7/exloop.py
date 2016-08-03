#!/usr/bin/env python
# exloop.py - raise exception to break loop

class ExitLoop(Exception): pass

try:
    for i in range(3):
        for j in range(3):
            if (i + j == 3):
                raise ExitLoop
except ExitLoop:
    print i, j
##################################################
#
#     $ exloop.py
#     1 2
#
