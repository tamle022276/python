#!/usr/bin/env python3
# temperature.py - Fahrenheit and Celsius converter

def farenheit(temp):
    ftemp = (9.0 / 5.0) * temp + 32
    return ftemp

def celsius(temp):
    ctemp = (5.0 / 9.0) * (temp - 32)
    return ctemp

if __name__ == "__main__":
   import sys
   if len(sys.argv) < 2:
      sys.stderr.write("Usage: temperature.py temp\n")
      sys.exit(1)

   temp = float(sys.argv[1])

   print("celsius to farenheit = %g " %farenheit(temp))
   print("farenheit to celsius = %g"  %celsius(temp))

###################################################

#    $ temperature.py 40
#    celsius to farenheit = 104 
#    farenheit to celsius = 4.44444

#    $ temperature.py -40
#    celsius to farenheit = -40 
#    farenheit to celsius = -40
#
