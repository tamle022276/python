#!/usr/bin/env python3
# testcommaformat.py - test comma formatting
import unittest
from CommaFormat import format

class TestCommaFormat(unittest.TestCase):
    def testEqual(self):
        self.assertEqual("123", format("123"))
        self.assertEqual("1,234", format("1234"))
        self.assertEqual("12,345", format("12345"))
        self.assertEqual("123,456", format("123456"))
        #self.assertEqual("1,234,567", format("1234567"))

if __name__ == "__main__":
   unittest.main()
