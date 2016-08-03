#!/usr/bin/env python
# mycircle1.py - Circle program
from Circle1 import Circle

c1 = Circle()                  # default Circle
c1.setRadius(10)               # call setter
print "radius = %g" %c1.getRadius()
print "area = %g" %c1.area()      

#################################################
#
#    $ mycircle1.py
#    radius = 10
#    area = 314.159
#
