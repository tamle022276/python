#!/usr/bin/env python3
# mytuple2.py - lists and tuples

mytuple = (45,23,101,[66,12,33],17,29)

mylist = list(mytuple)
mylist[3:4] = mylist[3]
mylist.sort()
mytuple = tuple(mylist)
print(mytuple)

##########################################

#    $ mytuple2.py
#    (12, 17, 23, 29, 33, 45, 66, 101)
