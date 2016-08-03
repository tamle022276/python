#!/usr/bin/env python
# loans.py - calculates compounding interest

def calc(principal, interest, years):
   interest /= 100
   for y in range(years):
      earnings = principal * interest
      principal += earnings
      print y+1, "(+%d)" %earnings, "=> %.2f" %principal
   return principal

