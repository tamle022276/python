#!/usr/bin/env python
# varargs2.py - variable argument dictionary

def makeDict(**args):
    print args

makeDict()
makeDict(key = 1, value = "one")
makeDict(key = 2, value = "two")
makeDict(key = 3, value = "three")

#####################################
#
#     $ varargs2.py
#     {}
#     {'value': 'one', 'key': 1}
#     {'value': 'two', 'key': 2}
#     {'value': 'three', 'key': 3}
#
