#!/usr/bin/env python
# checkargs.py - check argument assertions
import unittest

class CheckArgs(unittest.TestCase):
    def testEqual(self):
        s = "start"                # assert ok
        self.assertEqual(s[:-1], "star", "not first 4 chars")

    def testNotEqual(self):
        line = "alphabet"
        i = 5                      # assert fails
        self.assertNotEqual(line.find("bet"), i, "bad index") 

if __name__ == "__main__":
   unittest.main()

