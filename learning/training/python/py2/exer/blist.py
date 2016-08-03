#!/usr/bin/env python
# blist.py - Bounded list
from BArray import BArray

array = BArray(2000, 2009)
print "lower bound = %d" %array.lb()
print "upper bound = %d" %array.ub()
print "length is %d" %array.length()

val = 0
for index in array.getRange():
    array[index] = val              # setter
    val += 1

for index in array.getRange():
    print array[index],             # getter

#################################################
#
#    $ blist.py
#    lower bound = 2000
#    upper bound = 2009
#    length is 10
#    0 1 2 3 4 5 6 7 8 9
#
