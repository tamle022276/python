#!/usr/bin/env python
# mutable.py - mutable with only list, dict arguments

def assign(arg):
    if (type(arg) is list or type(arg) is dict):
        arg[0] = 10              # changes item
        arg[1] = "xyz"           # changes item

mylist = [1, "abc"]
assign(mylist)                   # changes mylist
print mylist

mydict = {0 : "zero", 1 : "one"}
assign(mydict)                   # changes mydict
print mydict

assign("abc")                    # ignored
assign(12)                       # ignored

#####################################
#
#     $ mutable.py
#     [10, 'xyz']
#     {0: 10, 1: 'xyz'}
#
