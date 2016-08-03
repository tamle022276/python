#!/usr/bin/env python3
# tryexcept.py - with exceptions

def getNum(): return 10

try:
    array = [1, 2, 3, 4, 5]
    index = getNum()
    print(array[index])
except IndexError:
    print("Illegal subscript", index)

###################################################
#
#     $ tryexcept.py
#     Illegal subscript 10
#
