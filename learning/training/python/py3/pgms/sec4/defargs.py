#!/usr/bin/env python3
# defargs.py - default arguments

def func(a, b=2, c=4):
    print("a =", a, "b =", b, "c =", c)

func(5)
func(1, 5)
func(8, c=6)
func(c=6, a=5)

#####################################
#
#     $ defargs.py
#     a = 5 b = 2 c = 4
#     a = 1 b = 5 c = 4
#     a = 8 b = 2 c = 6
#     a = 5 b = 2 c = 6
#
