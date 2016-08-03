#!/usr/bin/env python
# modargs.py - make immmutables mutable for indexing

def assign(arg1, arg2):
    arg1[0] = "j"
    arg2[1] = 10

mystring = "hello"                # immutable string
mytuple = (1, 2, 3)               # immutable tuple
#assign(mystring, mytuple)        # does not compile

mystring = list("hello")          # make string mutable
mylist = list(mytuple)            # make tuple mutable
assign(mystring, mylist)          # modifies args 
print mystring, mylist

#####################################
#
#     $ modargs.py
#     ['j', 'e', 'l', 'l', 'o'] [1, 10, 3]
#
