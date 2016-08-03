#!/usr/bin/env python3
# temp.py - temperature converter
import temperature

temp = 40

print(temp, "celsius is %g farenheit" %temperature.farenheit(temp))
print(temp, "farenheit is %g celsius" %temperature.celsius(temp))

###############################################
#
#    $ temp.py
#    40 celsius is 104 farenheit
#    40 farenheit is 4.44444 celsius
#
