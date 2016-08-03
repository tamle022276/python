#!/usr/bin/env python3
# testdescription.py - test descriptions
import unittest

class TextDescription(unittest.TestCase):
    def setUp(self):
        testname = self.shortDescription()
        if (testname == "Test 1"):
            print("In setup() for Test 1")
        elif (testname == "Test 2"):
            print("In setup() for Test 2")

    def tearDown(self):
        testname = self.shortDescription()
        if (testname == "Test 1"):
            print("In tearDown() for Test 1")
        elif (testname == "Test 2"):
            print("In tearDown() for Test 2")

    def test1(self):
        """ Test 1"""
        print("In test1()")

    def test2(self):
        """ Test 2"""
        print("In test2()")

if __name__ == "__main__":
   unittest.main()

