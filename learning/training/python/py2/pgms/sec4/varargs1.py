#!/usr/bin/env python
# varargs1.py - variable argument tuples

def makeTuple(*args):
    print args

makeTuple()
makeTuple(1.1)
makeTuple(1.1, 2.2)

makeTuple("one")
makeTuple("one", "two")

#####################################
#
#     $ varargs1.py
#     ()
#     (1.1,)
#     (1.1, 2.2)
#     ('one',)
#     ('one', 'two')
#
