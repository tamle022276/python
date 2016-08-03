#!/usr/bin/env python
# interest.py - calculates compounding interest

def calc(principal, interest, years):
   interest /= 100
   for y in range(years):
      earnings = principal * interest
      principal += earnings
      print y+1, "(+%d)" %earnings, "=> %.2f" %principal
   return principal

if __name__ == "__main__":     # run as main program?
   import sys
   if len(sys.argv) < 4:
      sys.stderr.write("Usage: interest.py cash rate time\n")
      exit(1)

   cash = int(sys.argv[1])
   rate = float(sys.argv[2])
   time = int(sys.argv[3])

   print "cash = ", cash
   print "interest = ", rate
   print "time period = ", time

   calc(cash, rate, time)

#################################################
#
#    $ interest.py 65000 5.5 5
#    cash =  65000
#    interest =  5.5
#    time period =  5
#    1 (+3575) => 68575.00
#    2 (+3771) => 72346.62
#    3 (+3979) => 76325.69
#    4 (+4197) => 80523.60
#    5 (+4428) => 84952.40
#
