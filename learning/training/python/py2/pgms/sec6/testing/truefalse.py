#!/usr/bin/env python
# truefalse.py - true and false assertions
import unittest

class TrueFalse(unittest.TestCase):
    def testTrue(self):
        title = "THIS IS IMPORTANT"     # assert ok
        self.assertTrue(title.isupper(), "not all uppercase")

    def testFalse(self):
        word = "   "                    # assert fails
        self.assertFalse(word.isspace(), "all spaces")

if __name__ == "__main__":
   unittest.main()

