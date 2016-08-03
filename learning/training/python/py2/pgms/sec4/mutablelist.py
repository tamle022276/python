#!/usr/bin/env python
# mutablelist.py - mutable list arguments

def assign(arg):
    arg[0] = 10              # changes list item
    arg[1] = "xyz"           # changes list item

mylist = [1, "abc"]
assign(mylist)               # changes mylist
print mylist

#####################################
#
#     $ mutablelist.py
#     [10, 'xyz']
#
