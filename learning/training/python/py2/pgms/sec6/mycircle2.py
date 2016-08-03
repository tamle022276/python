#!/usr/bin/env python
# mycircle2.py - Circle program
from Circle2 import Circle

c1 = Circle()                  # default Circle
print "radius = %g" %c1.getRadius()

c2 = Circle(10)                # create Circle
print "radius = %g" %c2.getRadius()
print "area = %g" %c2.area()

c3 = Circle(-10)                # bad radius
print "radius = %g" %c3.getRadius()

c3.setRadius(100)
print "area = %g" %c3.area()

#################################################
#
#    $ mycircle2.py
#    radius = 1
#    radius = 10
#    area = 314.159
#    radius = 1
#    area = 31415.9
#
