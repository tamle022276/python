#!/usr/bin/env python
# checkargs.py - check argument assertions
import unittest

class Thing: pass
class MyThing: pass

class CheckArgs(unittest.TestCase):
    def testObjects(self):
        one = Thing()
        two = MyThing()           # assert fails
        self.assertIs(one, two, "different objects") 

    def testInstances(self):
        one = Thing()
        two = MyThing()          # assert ok
        self.assertIsInstance(one, Thing, "not a Thing")

if __name__ == "__main__":
   unittest.main()

