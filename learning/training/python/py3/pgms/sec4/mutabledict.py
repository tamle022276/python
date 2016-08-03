#!/usr/bin/env python3
# mutabledict.py - mutable dictionary arguments

def assign(arg):
    arg["one"] = 1.0         # changes dict value
    arg["two"] = 2.0         # changes dict value

mydict = {"one" : 1, "two" : 2}
assign(mydict)               # changes mydict
print(mydict)

#####################################
#
#     $ mutabledict.py
#     {'two': 2.0, 'one': 1.0}
#
