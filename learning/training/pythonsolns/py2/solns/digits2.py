#!/usr/bin/env python
# digits2.py - one or two digit translator

def translate(num):
    tens = ("twenty", "thirty", "forty", "fifty", "sixty",
            "seventy", "eighty", "ninety")

    teens = ("ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
            "sixteen", "seventeen", "eighteen", "nineteen")

    ones = ("zero", "one", "two", "three", "four", "five",
            "six", "seven", "eight", "nine")

    if num <= 9:
        return ones[num]

    if num <= 19:
        return teens[num % 10]

    ten = tens[(num // 10)-2]
    one = " "
    if num % 10:
       one += ones[num % 10] 
    return ten + one

while True:
    num = int(raw_input("Input a number(0..99) "))
    if (num >= 0 and num <= 99):
        print translate(num)
    else:
        print num, "is invalid"
        break

##############################################
#
#     $ digits2.py
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

