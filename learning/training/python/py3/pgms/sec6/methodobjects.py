#!/usr/bin/env python3
# methodobjects.py - Bound and unbound methods

class MyClass:
    def myMethod(self, data):
        print(data)

obj = MyClass()                       # instance object
obj.myMethod("message one")           # invoke method

func = obj.myMethod                   # bound method
func("message two")                   # invoke bound method

var = MyClass.myMethod                # unbound method
var(obj, "message three")             # invoke method

#################################################
#
#    $ methodobjects.py
#    message one
#    message two
#    message three
#
