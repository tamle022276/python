#!/usr/bin/env python3
# typeid.py - class type indentification

class Base: pass
class Derived(Base): pass

base = Base()
derived = Derived()

print(base.__class__.__name__)
print(derived.__class__.__name__)
print(derived.__class__.__bases__)
 
print(isinstance(base, Base))             # True
print(isinstance(derived, Derived))       # True
print(isinstance(derived, Base))          # True

print(issubclass(Derived, Base))          # True
print(issubclass(Base, Derived))          # False
print(issubclass(Derived, Derived))       # True

#####################################
#
#     $ typeid.py
#     Base
#     Derived
#     (<class '__main__.Base'>,)
#     True
#     True
#     True
#     True
#     False
#     True
#
