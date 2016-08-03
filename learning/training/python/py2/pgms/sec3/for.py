#!/usr/bin/env python
# for.py - for statement

for s in ["One", "Two", "Three"]:
    print s,
print

for i in range(5):
    print i,
print

names = {"Bob" : "bob@gmail.com", "Art" : "art@aol.com"}

for (name, email) in names.items():
    print "Contact %s at %s" %(name, email) 

N = [2, 4, 6]
M = [3, 5, 7]

for (i, j) in zip(N, M):
    print i, "*", j, "=", i*j

##################################################
#
#     $ for.py
#     One Two Three
#     0 1 2 3 4
#     Contact Bob at bob@gmail.com
#     Contact Art at art@aol.com
#     2 * 3 = 6
#     4 * 5 = 20
#     6 * 7 = 42
#
