#!/usr/bin/env python3
# sequences.py - sequence assertions
import unittest

class Sequences(unittest.TestCase):
    def testList(self):
        evens = [2, 4, 6, 8]
        odds = [1, 3, 5, 9]            # assert fails
        self.assertListEqual(evens, odds, "lists not same")

    def testDict(self):
        D1 = {"one" : 1, "two" : 2}
        D2 = {"two" : 2, "one" : 1}    # assert ok
        self.assertDictEqual(D1, D2, "dictionaries not same")

    def testIn(self):
        list = [2, 4, 6, 8]
        val = 6                        # assert ok
        self.assertIn(val, list, "no item")

    def testTuple(self):
        nums = (2, 4, 6, 8)
        vals = (8, 6, 4, 2)            # assert fails
        self.assertTupleEqual(nums, vals, "tuples not same")

    def testItems(self):
        nums = (2, 4, 6, 8)
        vals = (8, 6, 4, 2)            # assert ok
        self.assertCountEqual(nums, vals, "not same items")

if __name__ == "__main__":
   unittest.main()

