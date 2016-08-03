#!/usr/bin/env python3
# methods.py - Invoking methods

class MyClass:
    def myInstanceMethod(self, data):
        print(self, data)

    def classMethod(cls, data):
        print(cls, data)

    def staticMethod(data):
        print(data)

    myClassMethod = classmethod(classMethod)
    myStaticMethod = staticmethod(staticMethod)

obj = MyClass()                       # make instance object

obj.myInstanceMethod(10)              # with instance object
MyClass.myInstanceMethod(obj, 20)     # with class name

MyClass.myClassMethod(30)             # with class name
obj.myClassMethod(40)                 # with instance object

MyClass.myStaticMethod(50)            # with class name
obj.myStaticMethod(60)                # with instance object

#################################################
#
#    $ methods.py
#    <__main__.MyClass instance at 0x95757cc> 10
#    <__main__.MyClass instance at 0x95757cc> 20
#    __main__.MyClass 30
#    __main__.MyClass 40
#    50
#    60
#
