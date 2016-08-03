#!/usr/bin/env python3
# forelse.py - for with else 

mylist = [12, 34.56, (10, 20), "abc"]
keys = [34.56, (10, 10)]

for key in keys:
    if key in mylist:
        print(key, "was found")
    else:
        print(key, "not found")

##################################################
#
#     $ forelse.py
#     34.56 was found
#     (10, 10) not found
#
