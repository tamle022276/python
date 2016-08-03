#!/usr/bin/env python3
# while.py - while statement
import sys

word = sys.argv[1]
list = ["Good", "Bad", "Ugly"]

while (list):
    if (list[0] == word):
        print(word)
        break
    list = list[1:]           # shift left
else:
    print(word, "not found")

###############################################
#
#      $ while.py Good
#      Good
#      $ while.py Beautiful
#      Beautiful not found
#
