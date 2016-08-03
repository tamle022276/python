#!/usr/bin/env python3
# abstract2.py - Abstract classes
from abc import ABCMeta, abstractmethod

class Super(metaclass=ABCMeta):
    def method(self):
        print("Super.method()", end=" ")
    @abstractmethod
    def whatType(self): pass
        #assert 0, "did not implement whatType()"

class Inherit(Super): pass         # no whatType()

class Replace(Super):
    def method(self):              # override method
        print("Replace.method()")
    def whatType(self):
        return "Replace"

class Extend(Super):
    def method(self):
        Super.method(self)         # extend method
        print("Extend.method()")
    def whatType(self):
        return "Extend"

for cls in [Replace(), Extend(), Inherit()]:
    print(cls.whatType(), ":", end="")
    cls.method()

#################################################
#
#    $ abstract2.py
#    Traceback (most recent call last):
#    File "./abstract2.py", line 27, in <module>
#    for cls in [Replace(), Extend(), Inherit()]:
#    TypeError: Can't instantiate abstract class Inherit with abstract methods 
#    whatType
#
