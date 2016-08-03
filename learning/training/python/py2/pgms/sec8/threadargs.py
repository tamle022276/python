#!/usr/bin/env python
# threadargs.py - thread arguments
from threading import Thread, currentThread

def myThread1(num):
    name = currentThread().getName()
    print name, num

def myThread2(num, id):
    name = currentThread().getName()
    print name, num, id

def myThread3(list, tuple, dict):
    name = currentThread().getName()
    print name, list, tuple, dict

th1 = Thread(target=myThread1, args=(10,))
th2 = Thread(target=myThread2, args=(10, "max"))

list = [2, 4, 6, 8]
tuple = (1, 3, 7, 9)
dict = {"bob" : 12, "sue" : 8}
th3 = Thread(target=myThread3, args=(list, tuple, dict))

th1.start(); th2.start(); th3.start()

##################################################
#
#     $ threadargs.py
#     Thread-1 10
#     Thread-2 10 max
#     Thread-3 [2, 4, 6, 8] (1, 3, 7, 9) {'bob': 12, 'sue': 8}
#
