#!/usr/bin/env python3
# scope1.py - scope rules

name = "scope"                   # name is global
num = 55                         # num is global

def myfunc(string):
    new = name + " " + string    # new, string are local
    num = 100                    # num local, hides global
    #num = num + 100             # UnboundLocalError
    new += " " + str(num)        # str is built-in
    return new

answer = myfunc("rules")         # answer is global
print(num)                       # prints 55
print(answer)                    # prints scope rules 100

#####################################
#
#     $ scope1.py
#     55
#     scope rules 100
#
