#!/usr/bin/env python
# if.py - if statement

c = raw_input("Enter an alpha char: ")

if (c >= '0' and c <= '9'):
    print "digit"
elif (c >= 'a' and c <= 'z'):
    print "lower case letter"
elif (c >= 'A' and c <= 'Z'):
    print "upper case letter"
else:
    print "invalid input"

##############################################
#
#     $ if.py
#     Enter an alpha char: 5
#     digit
#
#     $ if.py
#     Enter an alpha char: @
#     invalid input
#
