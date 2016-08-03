#!/usr/bin/env python3
# copylist.py - copy list argument

def assign(arg):
    arg[0] = 10              # changes list item
    arg[1] = "xyz"           # changes list item

mylist = [1, "abc"]
assign(mylist[:])            # won't change mylist
print(mylist)

#####################################
#
#     $ copylist.py
#     [1, 'abc']
