#!/usr/bin/env python
# nested.py - nested scope

def sayit():
    saying = "show me the money"
    def say():
        print saying
    say()

sayit()

#####################################
#
#     $ nested.py
#     show me the money
#      
#
