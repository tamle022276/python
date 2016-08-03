#!/usr/bin/env python
# testfixture.py - test fixture
import unittest

class TextFixture(unittest.TestCase):
    def setUp(self):
        print "In setup()"
        self.list = range(1, 5)

    def tearDown(self):
        print "In tearDown()"
        del self.list

    def test(self):
        print "In test()"
        self.assertEqual(self.list, range(1, 5))

if __name__ == "__main__":
   unittest.main()

