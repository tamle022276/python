#!/usr/bin/env python
# tuple.py - tuples

boys = ("joe", "bob", "dave")
girls = ("ann", "mary", "linda")
print boys + girls
print (2, 4) * 3
nums = (1, 2, 3, 4)
print nums[0], nums[1:3]
var = (40)
singleTuple = (40,)
print var, singleTuple

words = ("strong", "better", "many")
print len(words)
temp = list(words)
temp.sort()
words = tuple(temp)
print words

##############################################
#
#     $ tuple.py
#     ('joe', 'bob', 'dave', 'ann', 'mary', 'linda')
#     (2, 4, 2, 4, 2, 4)
#     1 (2, 3)
#     40 (40,)
#     3
#     ('better', 'many', 'strong')
#
