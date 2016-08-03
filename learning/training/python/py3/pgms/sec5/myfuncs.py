# myfuncs.py - set functions

def unique(arg):
    return list(set(arg))

def intersect(arg1, arg2):
    return list(set(arg1) & set(arg2))

def union(arg1, arg2):
    return list(set(arg1) | set(arg2))
