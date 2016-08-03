#!/usr/bin/env python
# branch.py - multi-way branch

number = 3

if (number == 1):
    print "one"
elif (number == 2):
    print "two"
elif (number == 3):
    print "three"
else:
    print "unknown number"

print {1 : "one", 2 : "two", 3 : "three"}[number]

branch = {1 : "one", 2 : "two", 3 : "three"}
print branch.get(2, "unknown number")
print branch.get(4, "unknown number")

##############################################
#
#     $ branch.py
#     three
#     three
#     two 
#     unknown number     
