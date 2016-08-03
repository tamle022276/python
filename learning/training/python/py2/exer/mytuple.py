#!/usr/bin/env python2.6
# mytuple.py - lists and tuples

mytuple = (45,23,101,[66,12,33],17,29)

# your code here...


temp = list(mytuple)
temp[3:4] = temp[3]
temp.sort()
mytuple = tuple(temp)


print mytuple

##########################################

#    $ mytuple.py
#    (12, 17, 23, 29, 33, 45, 66, 101)
