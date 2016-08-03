#!/usr/bin/env python3
# interest.py - calculates compounding interest

def calc(principal, interest, years):
   interest /= 100
   for y in range(years):
      earnings = principal * interest
      principal += earnings
      print(y+1, "(+%d)" %earnings, "=> %.2f" %principal)
   return principal

if __name__ == "__main__":     # run as main program?
   import doctest
   doctest.testfile("interest.txt")
