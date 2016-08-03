#!/usr/bin/env python
# noexcept.py - no exceptions
def getNum(): return 10

array = [1, 2, 3, 4, 5]
index = getNum()
print array[index]

###################################################
#
#     $ noexcept.py
#     Traceback (most recent call last):
#       File "./noexcept.py", line 7, in <module>
#         print array[index]
#     IndexError: list index out of range
