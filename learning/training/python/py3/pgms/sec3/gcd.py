#!/usr/bin/env python3
# gcd.py - greatest common divisor
import sys

num1 = int(sys.argv[1])       # first arg
num2 = int(sys.argv[2])       # second arg

while (num2 != 0):
    (num1, num2) = (num2, num1 % num2)
print(num1)

##########################################

#    $ gcd.py 8 12
#    4
#    $ gcd.py 24 54
#    6
#    $ gcd.py 121 1001
#    11
