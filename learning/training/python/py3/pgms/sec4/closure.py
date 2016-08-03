#!/usr/bin/env python3
# closure.py - closures

def sayit():
    saying = "show me the money"
    def say():
        print(saying)
    return say

action = sayit()
action()

#####################################
#
#     $ closure.py
#     show me the money
#      
#
