#!/usr/bin/env python
# testrunner.py - test runner
import unittest

class TestRunner(unittest.TestCase):
    def testDict(self):
        D1 = {"one" : 1, "two" : 2}
        D2 = {"two" : 2, "one" : 1}    # assert ok
        self.assertDictEqual(D1, D2, "dicts not same")

    def testIn(self):
        list = [2, 4, 6, 8]
        val = 6                        # assert ok
        self.assertIn(val, list, "no item")

    def testItems(self):
        nums = (2, 4, 6, 8)
        vals = (8, 6, 4, 2)            # assert ok
        self.assertItemsEqual(nums, vals, "diff items")

tests = unittest.TestLoader().loadTestsFromTestCase(TestRunner)
unittest.TextTestRunner(verbosity=2).run(tests)

