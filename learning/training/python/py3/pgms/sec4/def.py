#!/usr/bin/env python3
# def.py - def statements

flag = True
if flag:
    def myprint():
        print("do it this way")
else:
    def myprint():
        print("do it another way")
        
myprint()
myfunc = myprint
myfunc()

#####################################
#
#     $ def.py
#     do it this way
#     do it this way
#
