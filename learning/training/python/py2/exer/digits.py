#!/usr/bin/env python
# digits.py - one or two digit translator

def translate(num):
    # your code here...
    pass

while True:
    num = int(raw_input("Input a number(0..99) "))
    if (num >= 0 and num <= 99):
        print translate(num)
    else:
        print num, "is invalid"
        break

##############################################
#
#     $ digits.py
#     Input a number(0..99) 18 
#     eighteen
#     Input a number(0..99) 39 
#     thirty nine
#     Input a number(0..99) 61 
#     sixty one
#     Input a number(0..99) 80 
#     eighty
#     Input a number(0..99) 100 
#     100 is invalid 
#     $

