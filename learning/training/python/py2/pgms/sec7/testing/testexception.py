#!/usr/bin/env python
# testexception.py - test exceptions
import unittest

def raise_error(arg):
    print arg
    raise ValueError("Bad value: " + str(arg))

class TestException(unittest.TestCase):
    def testWithException(self):
        self.failUnlessRaises(ValueError, raise_error, 12)

if __name__ == "__main__":
   unittest.main()

