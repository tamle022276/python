#!/usr/bin/env python3
# scope2.py - scope rules

name = "scope"                   # name is global
num = 55                         # num is global

def myfunc(str):                 # THIS HIDES str BUILT-IN
    new = name + " " + str       # new, str are local
    num = 100                    # num local, hides global
    new += " " + str(num)        # str is built-in
    return new

answer = myfunc("rules")         # answer is global
print(num)                       # prints 55
print(answer)                    # prints scope rules 100

#####################################
#
#     $ scope2.py
#     Traceback (most recent call last):
#     File "./scope2.py", line 13, in <module>
#     answer = myfunc("rules")         # answer is global
#     File "./scope2.py", line 10, in myfunc
#     new += " " + str(num)        # str is built-in
#     TypeError: 'str' object is not callable
#
