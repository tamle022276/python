#!/usr/bin/env python
# testperfectnum.py - test perfect numbers
import unittest
from PerfectNumber import isPerfect

class TestPerfectNumber(unittest.TestCase):
    def testEqual(self):
        self.assertTrue(isPerfect(28), "not a perfect number")
        self.assertTrue(isPerfect(496), "not a perfect number")
        self.assertTrue(isPerfect(8128), "not a perfect number")
        self.assertTrue(isPerfect(33550336), "not a perfect number")

if __name__ == "__main__":
   unittest.main()
