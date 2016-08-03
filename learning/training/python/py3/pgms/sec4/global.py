#!/usr/bin/env python3
# global.py - global statement

name = "scope"                   # name is global
num = 55                         # num is global

def myfunc(string):
    new = name + " " + string    # new, string are local
    global num                   # global statement
    num = 100                    # accesses global num
    new += " " + str(num)        # str is built-in
    return new

answer = myfunc("rules")         # answer is global
print(num)                       # prints 100
print(answer)                    # prints scope rules 100

#####################################
#
#     $ global.py
#     100
#     scope rules 100
#
