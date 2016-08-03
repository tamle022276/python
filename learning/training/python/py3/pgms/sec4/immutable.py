#!/usr/bin/env python3
# immutable.py - immutable arguments

def assign(a1, a2, a3, a4, a5):
    a1 = 10                  # local int
    a2 = "ten"               # local string
    a3 = 67.89               # local float
    a4 = 3.3 + 4.4j          # local complex
    a5 = (5, 6, 7, 8)        # local tuple


i = 34; s = "one"; f = 34.56; c = 1.1 + 2.2j  
t = (1, 2, 3, 4)

assign(i, s, f, c, t)        # no changes to any args
print(i, s, f, c, t)

#####################################
#
#     $ immutable.py
#     34 one 34.56 (1.1+2.2j) (1, 2, 3, 4)
