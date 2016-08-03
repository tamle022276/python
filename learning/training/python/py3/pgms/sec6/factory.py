#!/usr/bin/env python3
# factory.py - Class factories
import sys

class Thing:
    def method(self):
        print("Thing")

class OtherThing:
    def method(self):
        print("OtherThing")

def factory(className):
    instance = globals()[className]
    return instance()

className = sys.argv[1]

var = factory(className)
var.method()

#################################################
#
#    $ factory.py Thing
#    Thing
#
#    $ factory.py OtherThing
#    OtherThing
