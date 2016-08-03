#!/usr/bin/env python
# indexer.py - Method overloading

class Indexer:
    def __getitem__(self, index):
        return index ** 3

list = range(11)
for index in list:
    print list[index],
print

cubes = Indexer()
for index in range(11):
    print cubes[index],

#################################################
#
#    $ indexer.py
#    0 1 2 3 4 5 6 7 8 9 10
#    0 1 8 27 64 125 216 343 512 729 1000
#
