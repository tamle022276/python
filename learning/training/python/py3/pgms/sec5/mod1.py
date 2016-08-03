#!/usr/bin/env python3
# mod1.py - module 1
import mod2

def f():
    print("module 1")

f()
mod2.f()
mod2.mod3.f()

#####################################
#
#     $ mod1.py
#     module 2
#     module 3
#     module 1
#     module 2
#     module 3
#
