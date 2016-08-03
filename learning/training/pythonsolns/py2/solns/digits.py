#!/usr/bin/env python
# digits.py - one or two digit translator

def translate(num):
    specials = { 0:"zero", 11:"eleven", 12:"twelve", 13:"thirteen", 14: "fourteen",
                15:"fifteen", 16:"sixteen", 17:"seventeen", 18:"eighteen", 19:"nineteen" }

    ones = { 0:"", 1:"one", 2:"two", 3:"three", 4:"four", 5:"five", 6:"six",
              7:"seven", 8:"eight", 9:"nine" }

    tens = { 1:"ten", 2:"twenty", 3:"thirty", 4:"forty", 5:"fifty", 6:"sixty",
                 7:"seventy", 8:"eighty", 9:"ninety" }

    if (num in specials):
        return specials[num]

    if (num < 10):
        return ones[num]

    one = ones[num % 10]
    ten = tens[num // 10]
    return ten + " " + one
    
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

