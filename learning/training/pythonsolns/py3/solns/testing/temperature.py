#!/usr/bin/env python3
# temperature.py - Fahrenheit and Celsius converter

def farenheit(temp):
    ftemp = (9.0 / 5.0) * temp + 32
    return ftemp

def celsius(temp):
    ctemp = (5.0 / 9.0) * (temp - 32)
    return ctemp

if __name__ == "__main__":
   import doctest
   doctest.testfile("temperature.txt")
