#!/usr/bin/env python3
# abstract.py - Abstract classes

class Super:
    def method(self):
        print("Super.method()", end=" ")
    def whatType(self):
        assert 0, "did not implement whatType()"

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
#    $ abstract.py
#    Replace : Replace.method()
#    Extend : Super.method() Extend.method()
#    Traceback (most recent call last):
#    File "./abstract.py", line 26, in <module>
#    print(cls.whatType(), ":", end="")
#    File "./abstract.py", line 8, in whatType
#    assert 0, "did not implement whatType()"
#    AssertionError: did not implement whatType()
#
