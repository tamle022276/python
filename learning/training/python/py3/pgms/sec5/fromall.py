#!/usr/bin/env python3
# fromall.py - from * statement
from sys import *

print("You have", len(argv[1:]), "arguments")
for i in argv[1:]:
    print(i, end=" ")
print()
print("Python platform:", platform)

##############################################
#
#     $ fromall.py one two three
#     You have 3 arguments
#     one two three
#     Python platform: linux2
#
#
